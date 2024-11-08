from model.primitives import (
    Cell, 
    InfillGraph
)
import os 

from model.model3d import ModelData
from model.slicer import Slicer

from model.gcodewriter import GCodeWriter
from constants import *
import logging

logger = logging.getLogger(LOGGER)

class Model:
    def __init__(self):
        self.cell = None
        self.infill_graph = None
        self.gcode_writer = None
        self.model3d = ModelData()
        pass

    def update(self, file_path):
        logger.info("Loading "+file_path)
        self.cell = Cell(file_path)
        logger.info("Loaded "+file_path)

    def update_model3d(self, file_path, sliceProgBar, allowPerimeter):
        if not os.path.isfile(file_path):
            logger.info("ERROR"+ f'Your input 3d object file {file_path} not existed')
            return False
        
        self.model3d.read_file(file_path)
        if self.model3d.points.minz > 0 or self.model3d.points.minz < 0:
            logger.info("INFO"+ "+ Re-level model {:.3f}".format(-self.model3d.points.minz))
            self.model3d.translate([0, 0, -self.model3d.points.minz])
        manifold = self.model3d.check_manifold(verbose=False)
        if manifold:
            logger.info("WARN"+ "{} is manifold.".format(file_path))

        self.sliceProgBar = sliceProgBar
        self.init_slicer(prog_bar=sliceProgBar, enable_perims=allowPerimeter)
        logger.info("Loaded "+ file_path + " and init slicer successful") 
    
    def init_slicer(self, prog_bar, enable_perims):
        self.slicer = Slicer([self.model3d], logger=logger,
                             prog_bar=prog_bar,
                             enable_perims=enable_perims)

    def handle_progbar_signal(self, value):
        self.sliceProgBar.setValue(value)

    def get_layers_items(self):
        return self.infill_graph.get_plot_comb_num()

    def split_layers(self, n: int, x: int, y: int):
        logger.info("Splitting layers...")
        self.infill_graph = InfillGraph(self.cell, x, y)
        self.infill_graph.combine_cycle(n)
        logger.info("Finished splitting.")

    def generate_printpath(self, split_id, rows, cols, setting, offset, scale, num_layers, printer):
        logger.info("Generating infill print path from unit cell split...")
        path_dicts = self.infill_graph.get_infill_paths(split_id, 1)
        self.gcode_writer = GCodeWriter(
            path_dicts=path_dicts, 
            cell_width=self.infill_graph.width, cell_height=self.infill_graph.height,
            rows=rows, cols=cols
        )
        self.gcode_writer.setup(setting=setting, offset=offset, scale=scale, num_layers=num_layers, printer=printer)
        self.gcode_writer.make_steps()
        logger.info("Finished generating infill print path from unit cell split.")
    
    def generate_preview(self):
        logger.info("Updating print preview...")
        html = self.gcode_writer.plot()
        logger.info("Finished updating print preview.")
        return html
    
    def save_gcode(self, filename):
        self.gcode_writer.save_gcode(filename)
        
    def get_cell_plot(self):
        if not self.cell:
            return lambda *arg: None
        return self.cell.plot_preview
    
    def get_model_plot(self):
        if not self.model3d:
            return lambda *arg: None
        return self.model3d.plot_preview3d

    def get_layers_plot(self):
        if len(self.infill_graph.cycle_comb_list) == 0:
            return lambda *arg: None
        return self.infill_graph.plot_comb