from __future__ import print_function

import math
import time
import datetime
import random

from conf.config import slicer_configs
from utils.config_parser import load_printing_schedule
import model.geometry2d as geom

from PySide6.QtCore import Signal, QObject
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

    def slice_to_file(self, setting, filename=''):
        st = time.time()
        self.raw_layer_paths = {}
        
        self.dflt_nozl = self.conf['default_nozzle']

        self.center_point = (self.conf['bed_center_x'], self.conf['bed_center_y'])
        
         # Dùng giá trị trong config
        dflt_nozl_d = self.conf['nozzle_{0}_diam'.format(self.dflt_nozl)]
        # self.layer_h = self.conf['layer_height']
        
        self.extrusion_ratio = self.conf['nozzle_{0}_flow_rate'.format(self.dflt_nozl)]
        self.extrusion_width = dflt_nozl_d * self.extrusion_ratio
        self.infill_width = dflt_nozl_d * self.extrusion_ratio

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

        if self.logger is not None:
            self.logger.info("Start compute the object's perimeter")
        self._slicer_task_perimeters()
        
        self.prog_bar_signal.setValue(0)

        if self.logger is not None:
            self.logger.info("Start compute the object infill")
        print("--> Infill computing")
        self._slicer_task_fill()
        
        self.prog_bar_signal.setValue(50)

        if self.logger is not None:
            self.logger.info("Start compute the pathing for extruders")
        print("--> Pathing computing")
        self._slicer_task_pathing()
        
        self.prog_bar_signal.setValue(75)

        if self.logger is not None:
            self.logger.info("Generate the GCode")
        print("--> Export GCode to \"{}\"".format(filename))

        self.gcode_data = self._slicer_task_gcode(filename)
        
        self.prog_bar_signal.setValue(100)

        if filename != '':
            self.write_gcode_to_file(self.gcode_data, filename)

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
            # Layer Slicing
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
            perims = self.perimeter_paths[layer]
            self.logger.info(f"Slicing layer {layer}")
            self._slicer_infill_one_layer(layer=layer, perims=perims)

    def _slicer_infill_one_layer(self, layer, perims):
        try:
            mask = perims[0][0]
            lines = self.model.get_model3d_infill_layer(layer)
            # if layer<4:
            #     print(mask)
            #     print('\n\n')
            #     print(lines)
            #     print('###########################\n\n')
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

    def write_gcode_to_file(self, gcode_data, filename):
        with open(filename, 'w') as f:
            f.write('\n'.join(gcode_data))

    def _slicer_task_gcode(self, filename):
        total_layers = self.layers

        self.model.gcode_writer.save_gcode2(self.raw_layer_paths, filename='__test1__.gcode')
        
        gcode_lines = []

        gcode_lines.append(";FLAVOR:Marlin")
        gcode_lines.append(";Layer height: {:.2f}".format(self.conf['layer_height']))

        if self.conf['gcode_comments']:
            gcode_lines.append(";generated by {:s} {:s} at {} from \"{:s}\"".format(self.NAME, self.VERSION,
                                                                                    datetime.datetime.now(),
                                                                                    ""))
        for k, v in sorted(self.conf.items()):
            if type(v) == str:
                v = v.replace("\n", '\\n')
            gcode_lines.append(";  {:s} = {}".format(k, v))

        gcode_lines.extend(["M82 ;absolute extrusion mode",
                            "G21 ;metric values",
                            "G90 ;absolute positioning",
                            "M107 ;Fan off"])

        if self.conf['bed_temp'] > 0:
            gcode_lines.extend(["M140 S{:d} ;set bed temp".format(self.conf['bed_temp']),
                                "M190 S{:d} ;wait for bed temp".format(self.conf['bed_temp'])])

        gcode_lines.append("M104 S{:d} ;set extruder0 temp".format(self.conf['nozzle_0_temp']))

        start_gcode = ";start gcode\n" + self.conf['start_gcode'].replace(r'\n', "\n") + "\n;/start gcode"
        gcode_lines.append(start_gcode)

        gcode_lines.extend(["M109 S{:d} ;wait for extruder0 temp".format(self.conf['nozzle_0_temp']),
                            "G92 E0 ;Zero extruder",
                            "M117 Printing...",
                            ";LAYER_COUNT:{}".format(total_layers)])

        for layer in range(total_layers):
            if self.conf['gcode_comments']:
                gcode_lines.append(";LAYER:{}".format(layer))
                gcode_lines.append("G00 Z")

            if layer in self.raw_layer_paths:
                layer_paths = self.raw_layer_paths[layer] # It consists of nsubLayer of each layer
                paths_data = layer_paths[0]
                typ = layer_paths[1]
               
                for line in self._paths_gcode(paths_data, layer, self.layer_zs[layer], typ): 
                    gcode_lines.append(line)

        end_gcode = ";end gcode\n" + self.conf['end_gcode'].replace(r'\n', "\n") + "\n;/end gcode"
        gcode_lines.append(end_gcode)

        return gcode_lines

    ###################################################################################################################
    def _vdist(self, a, b):
        delta = [x - y for x, y in zip(a, b)]
        dist = math.sqrt(sum([float(x) * float(x) for x in delta]))
        return dist

    def _add_raw_layer_paths(self, layer, paths, typ):

        self.raw_layer_paths[layer] = [paths, typ]

    def _paths_gcode(self, paths, layer, z, typ=''):
        if len(paths) <= 0:
            return []

        # -- copy some configs into local vars
        nozl = 1
        fil_diam = self.conf['nozzle_{0:d}_filament'.format(nozl)]
        nozl_diam = self.conf['nozzle_{0:d}_diam'.format(nozl)]
        max_speed = self.conf['nozzle_{0:d}_max_speed'.format(nozl)]
        feed_rate = self.conf['nozzle_{0:d}_feed_rate'.format(nozl)]
        extrusion_ratio = self.conf['nozzle_{0:d}_flow_rate'.format(nozl)]
        layer_height = self.conf['layer_height']
        travel_rate_xy = self.conf['travel_rate_xy']
       
        # -- calculating some extrusion factor
        ewidth = nozl_diam * extrusion_ratio 
        min_edist = nozl_diam / 2  # -- minimal edist based on nozl_diam
        speedf = 1

        if typ == 'perimeter' and self.conf['shell_speed'] > 0:  # -- perimeters may have their own speed
            speedf = self.conf['shell_speed'] / max_speed
            if typ == 'perimeter':  # -- FIXME: check for last (outer) perimeter/shell
                speedf = self.conf['external_shell_speed'] / max_speed

        xsect = math.pi * ewidth / 2 * layer_height / 2  
        fil_xsect = math.pi * fil_diam / 2 * fil_diam / 2
        xsectf = xsect / fil_xsect

        gcode_lines = []

        if len(paths) > 0 and self.conf['gcode_comments']:
            gcode_lines.append(";SPEED:{:.0f}%".format(speedf * 100))
            gcode_lines.append(";TYPE:" + typ.upper() + "")
        
        # -- all paths of single Z layer (z)
        path = paths[0]
        ox, oy = path[0:2]  # -- origin coord, z disregarded (comes as argument)

        dist = math.hypot(self.last_pos[1] - oy, self.last_pos[0] - ox)  # -- distance to move (from last pos)
        self.total_build_time += dist / travel_rate_xy

        gcode_lines.append("G0 X{x:.2f} Y{y:.2f} F{f:g}".format(x=ox, y=oy, f=travel_rate_xy * 60.0))
    
        for x, y in paths[1:]:  # -- now we process the rest of the path
            dist = math.hypot(y - oy, x - ox)

            fil_dist = dist * xsectf

            self.total_build_time += dist / feed_rate
            self.last_e += fil_dist

            gcode_lines.append("G1 X{x:.2f} Y{y:.2f} E{e:.3f}".format(x=x, y=y, e=self.last_e))
            self.last_pos = (x, y, z)
            ox, oy = x, y

        return gcode_lines