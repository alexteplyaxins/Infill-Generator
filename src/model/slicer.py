from __future__ import print_function

import math
import time
import datetime
import random

from conf.config import slicer_configs
from utils.config_parser import load_printing_schedule
import model.geometry2d as geom

from PySide6.QtCore import QObject
from conf.config import CONFIG_FILE
from utils.config_parser import ConfigParser

from model.model import Model
############################################################
class Slicer(QObject):

    
    def __init__(self, model: Model, logger=None, prog_bar=None,
                 enable_perims=None, zheight=0,
                 **kwargs):
        
        super().__init__()
        
        self.cell = model.cell
        self.model = model
        self.infill_graph = model.infill_graph
        self.model3d = model.data3d
        self.layer_h = zheight

        self.logger = logger
        self.prog_bar_signal = prog_bar
        self.enable_perims = enable_perims
        self.conf = {}
        self.conf_metadata = {}
        
        self.config_parser = ConfigParser(logger=self.logger, conf=self.conf, conf_metadata=self.conf_metadata)
        self.config_parser.load_configs()  
        self.last_pos = (0.0, 0.0, 0.0)
        self.last_e = 0.0
        self.last_nozl = -1 #Sua 231022
        self.total_build_time = 0.0
        self.mag = 4
        self.layer = 0
        self.last_typ = ''
        self.last_retract_typ = ''
        self.config(**kwargs)
        self.NAME = 'SUN3000'
        self.VERSION = '1'
        
        self.print_plan = load_printing_schedule()
        
        self.raw_layer_paths = {}
        self.gcode_data = []

    def config(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.conf:
                self.conf[key] = val

    def slice_to_file(self, filename='gcodefile'):
        st = time.time()
        self.raw_layer_paths = {}

        self.center_point = (self.conf['bed_center_x'], self.conf['bed_center_y'])

        model = self.model3d
        model.center(
                (self.center_point[0], self.center_point[1], (model.points.maxz - model.points.minz) / 2.0))
        model.assign_layers(self.layer_h)

        height = max([model.points.maxz - model.points.minz])
        self.layers = int(height / self.layer_h)
        self.layer_zs = [
            self.layer_h * (layer + 1)
            for layer in range(self.layers)
        ]
        
        self.prog_map = [int(100*i/self.layers) for i in range(self.layers)]

        self.prog_bar_signal.setValue(0)
        if self.logger is not None:
            self.logger.info("Start compute the object's perimeter")
        self._slicer_task_perimeters()
        
        self.prog_bar_signal.setValue(0)
        if self.logger is not None:
            self.logger.info("Start compute the object infill")
        self._slicer_task_fill()
        
        self.prog_bar_signal.setValue(0)
        if self.logger is not None:
            self.logger.info("Start compute the pathing for extruders")
        self._slicer_task_pathing()

        if self.logger is not None:
            self.logger.info("Generate the GCode")
        
        self.gcode_data = self._slicer_task_gcode()
        self.prog_bar_signal.setValue(100)

        msg = "Took {:.02f}s total. Estimated build time: {:d}h {:02d}m, filament used: {:.03f}m, layers: {:d}".format(
                time.time() - st,
                int(self.total_build_time / 3600),
                int((self.total_build_time % 3600) / 60),
                self.last_e / 1000,
                self.layers
            )
        if self.logger is not None:
            self.logger.info(msg)
        else:
            print(msg)


    ###################################################################################################
    def _slicer_task_perimeters(self):
        self.perimeter_paths = []
        
        
        for layer in range(self.layers):
            self.prog_bar_signal.setValue(self.prog_map[layer])
            
            # Layer slicing
            z = self.layer_zs[layer]
            paths = []
            model = self.model3d
            model_paths, dead = model.slice_at_z(z - self.layer_h / 2, self.layer_h)
            paths = geom.union(paths, model_paths)

            # Perimeters
            perims = []
            randpos = random.random()
            for i in range(self.conf['shell_count']):
                shell = geom.offset(paths, 0)
                shell = geom.close_paths(shell)
                if self.conf['random_starts']:
                    shell = [
                        (path if i == 0 else (path[i:] + path[1:i + 1]))
                        for path in shell
                        for i in [int(randpos * (len(path) - 1))]
                    ]
                perims.insert(0, shell)
            self.perimeter_paths.append(perims)

    def _slicer_task_fill(self):
        self.solid_infill = []
        self.sparse_infill = {}

        for layer in range(self.layers):
            self.prog_bar_signal.setValue(self.prog_map[layer])
            perims = self.perimeter_paths[layer]
            self.logger.info(f"Slicing layer {layer}")
            self._slicer_infill_one_layer(layer=layer, perims=perims)

    def _slicer_infill_one_layer(self, layer, perims):
        try:
            mask = perims[0][0]
            lines = self.model.get_model3d_infill_layer(layer)
            if layer<13 and layer>8:
                print(mask)
                print('\n\n')
                print(lines)
                print('###########################\n\n')
            path = self.model.clip_paths(mask, lines)
            if path:
                self.sparse_infill[layer] = path
            else:
                print(f"Cannot clipping path in layers {layer}")

        except Exception as e:
            print("Error in _slicer_infill_one_layer", e)
    
    def _slicer_task_pathing(self):
        for slice_num in range(len(self.perimeter_paths)):
            self.__slicer_task_pathing_perim(slice_num)
            self.__slicer_task_pathing_infill(slice_num)

    def __slicer_task_pathing_infill(self, slice_num):
        layer = slice_num
        layer_infills = self.sparse_infill[layer]
        self._add_raw_layer_paths(layer, layer_infills, 'infill')

    def __slicer_task_pathing_perim(self, slice_num):
        for paths in self.perimeter_paths[slice_num]:
            paths = geom.close_paths(paths)
            self._add_raw_layer_paths(slice_num, paths, 'perimeter')

    def _slicer_task_gcode(self):
        gcode_lines = self.model.gcode_writer.save_gcode2(self.raw_layer_paths, '__test1__.gcode', self.prog_bar_signal)
        return gcode_lines

    ###################################################################################################################
    def _vdist(self, a, b):
        delta = [x - y for x, y in zip(a, b)]
        dist = math.sqrt(sum([float(x) * float(x) for x in delta]))
        return dist

    def _add_raw_layer_paths(self, layer, paths, typ):

        self.raw_layer_paths[layer] = [paths, typ]