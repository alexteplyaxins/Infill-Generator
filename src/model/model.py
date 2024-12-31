from model.primitives import (
    Cell, 
    InfillGraph
)
import os 
from math import *

from model.model3d import ModelData

from model.gcodewriter import GCodeWriter

from constants import *
import logging

from model.grid1 import GridInfill 

logger = logging.getLogger(LOGGER)

class Model:
    def __init__(self):
        self.cell = None
        self.infill_graph = None
        self.gcode_writer = None
        self.path_dict = None
        self.data3d = None
        self.model3d_infill = None
        self.model3d_infill_dicts = []
        self.split_id = None
        pass

    def update(self, file_path, scale):
        logger.info("Loading "+file_path)
        self.cell = Cell(file_path, scale)
        logger.info("Loaded "+file_path)

    def update_model3d(self, file_path):
        if not os.path.isfile(file_path):
            logger.info("ERROR"+ f'Your input 3d object file {file_path} not existed')
            return False
        
        self.data3d = ModelData()
        self.data3d.read_file(file_path)
        self.gen_bounding_infill(1)

        if self.data3d.points.minz > 0 or self.data3d.points.minz < 0:
            logger.info("INFO"+ "+ Re-level model {:.3f}".format(-self.data3d.points.minz))
            self.data3d.translate([0, 0, -self.data3d.points.minz])
        logger.info("Loaded "+ file_path + " and init slicer successful") 

    def get_layers_items(self):
        return self.infill_graph.get_plot_comb_num()

    def split_layers(self, n: int, x: int, y: int):
        self.n = n
        logger.info("Splitting layers...")
        self.infill_graph = InfillGraph(self.cell, x, y)
        self.infill_graph.combine_cycle(n)
        logger.info("Finished splitting.")

    def generate_printpath(self, split_id, rows, cols, setting, offset, scale, num_layers, printer):
        logger.info("Generating infill print path from unit cell split...")
        self.path_dicts = self.infill_graph.get_infill_paths(split_id, 1)
        self.gcode_writer = GCodeWriter(
            path_dicts=self.path_dicts, 
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
    
    def get_layers_plot(self):
        if len(self.infill_graph.cycle_comb_list) == 0:
            return lambda *arg: None
        return self.infill_graph.plot_comb
    
    def gen_bounding_infill(self, scale):
        bx, by, bz = self.data3d.bounding_box()
        padding = 0
        width = bx[1]-bx[0] + padding
        height = by[1]-by[0] + padding
        self.model3d_infill = GridInfill(self.cell, self.infill_graph, width, height, self.split_id)

    def get_model3d_infill_layer(self, layer):
        return self.model3d_infill.get_grid(layer)

    def _line_intersection(self, p1, p2, mask, epsilon=1e-10):
        """ Return the intersection point of two line segments (p1,p2) and (p3,p4) using floats with precision control """
        s1_x = p2[0] - p1[0]
        s1_y = p2[1] - p1[1]
        n = len(mask)
        
        for i in range(n):
            p3 = mask[i]
            p4 = mask[(i + 1) % n]
            s2_x = p4[0] - p3[0]
            s2_y = p4[1] - p3[1]

            denominator = -s2_x * s1_y + s1_x * s2_y
            if abs(denominator) < epsilon:
                continue  # Skip nearly parallel or coincident lines

            s = (-s1_y * (p1[0] - p3[0]) + s1_x * (p1[1] - p3[1])) / denominator
            t = (s2_x * (p1[1] - p3[1]) - s2_y * (p1[0] - p3[0])) / denominator

            if -epsilon <= s <= 1 + epsilon and -epsilon <= t <= 1 + epsilon:
                # Calculate intersection point
                intersection_x = p1[0] + (t * s1_x)
                intersection_y = p1[1] + (t * s1_y)
                return (round(intersection_x, 10), round(intersection_y, 10))  # Control float precision
        return None

    def _is_in_poly(self, point, polygon):
        """Determines if a point is inside a polygon using the ray-casting algorithm.
        
        Args:
            point (tuple): The point as (x, y) coordinates.
            polygon (list): A list of vertices of the polygon [(x1, y1), (x2, y2), ...].
        
        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        x, y = point
        n = len(polygon)
        inside = False

        # Loop through each edge of the polygon
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]  # Next vertex (wraps around to the first vertex)
            
            # Check if the ray crosses the edge 
            if min(y1, y2) < y <= max(y1, y2) and x <= max(x1, x2):
                # Compute the intersection point of the edge with the horizontal ray at y
                if y1 != y2:
                    x_intersect = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                if x1 == x2 or x <= x_intersect:
                    inside = not inside

        return inside
    
    def clip_paths(self, mask, lines):
        npath = []
        
        lj = 0
        n = len(lines)
        for lj in range(0, n-1):
            if not self._is_in_poly(lines[lj], mask):
                if self._is_in_poly(lines[(lj + 1)%n], mask):
                    # chen giao diem
                    npath.append(self._line_intersection(lines[lj], lines[lj+1], mask))

            else: # diem dang xet dang o trong
                npath.append(lines[lj])
                if not self._is_in_poly(lines[lj + 1], mask):
                    npath.append(self._line_intersection(lines[lj], lines[lj+1], mask))
        return npath
