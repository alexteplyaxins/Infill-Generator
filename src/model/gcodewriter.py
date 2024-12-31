from model.grid import path_dict_2_grid
from model.gcodeplot import get_plot_html
import fullcontrol.gcode.primer_library

import plotly.graph_objects as go

import fullcontrol as fc
from fullcontrol.visualize.state import State
from fullcontrol.visualize.plot_data import PlotData
from fullcontrol.visualize.controls import PlotControls
from fullcontrol.visualize.tips import tips


class GCodeWriter:
    def __init__(self, path_dicts, cell_width, cell_height, cols, rows, layer_height=0.2):
        self.layers = [path_dict_2_grid(p, cols, rows, cell_width, cell_height) for p in path_dicts]
        self.layer_height = layer_height
    
    def get_distance(self, point1, point2):
        return abs(point1[0]-point2[0]) + abs(point1[1]-point2[1])
    
    def setup(self, setting, offset, scale, num_layers, printer):
        self.setting = setting
        self.layer_height = self.setting.get("extrusion_height", self.layer_height)
        self.num_layers = num_layers
        self.printer = printer
        self.offset = offset
        self.scale = scale

    def make_steps(self):
        steps = []
        offset_x = self.offset[0]
        offset_y = self.offset[1]
        current = self.offset
        initial_z = 0.6*self.layer_height
        
        steps.append(fc.Extruder(on=False))
        steps.append(fc.Point(x=offset_x, y=offset_y, z=initial_z))
        
        for i in range(self.num_layers):
            layer = [(x*self.scale+offset_x, y*self.scale+offset_y) for x, y in self.layers[i%len(self.layers)]]
            if self.get_distance(current, layer[0]) > self.get_distance(current, layer[-1]):
                layer = layer[::-1]
            steps.append(fc.Point(x=layer[0][0], y=layer[0][1], z=initial_z+i*self.layer_height))
            steps.append(fc.Extruder(on=True))
            for point in layer[1:]:
                steps.append(fc.Point(x=point[0], y=point[1]))
            current = point
            steps.append(fc.Extruder(on=False))
        
        self.steps = steps

    def plot(self, show_tips: bool = False):
        plot_controls = PlotControls(style='tube', zoom=0.7, printer_name=self.printer, initialization_data=self.setting)
        plot_controls.initialize()
        if show_tips: tips(plot_controls)

        state = State(self.steps, plot_controls)
        plot_data = PlotData(self.steps, state)
        for step in self.steps:
            step.visualize(state, plot_data, plot_controls)
        plot_data.cleanup()
        return get_plot_html(plot_data, plot_controls)
    
    def save_gcode(self, filename):
        gcode = fc.transform(self.steps, 'gcode', fc.GcodeControls(printer_name=self.printer, initialization_data=self.setting))
        with open(filename, "w") as file:
            file.write(gcode)

    def save_gcode2(self, layers, filename, progres_bar):
        steps = []
        offset_x = self.offset[0]
        offset_y = self.offset[1]
        initial_z = 0.6*self.layer_height
        
        steps.append(fc.Extruder(on=False))
        steps.append(fc.Point(x=offset_x, y=offset_y, z=initial_z))

        prog_map = [int(100*i/len(layers)) for i in range(len(layers))]
        for i in range(len(layers)):

            progres_bar.setValue(prog_map[i])
            layer = [(x*self.scale+offset_x, y*self.scale+offset_y) for x, y in layers[i][0]]
            steps.append(fc.Point(x=layer[0][0], y=layer[0][1], z=initial_z+i*self.layer_height))
            steps.append(fc.Extruder(on=True))
            for point in layer:
                steps.append(fc.Point(x=point[0], y=point[1]))
            steps.append(fc.Extruder(on=False))

        self.steps2 = steps
        gcode = fc.transform(self.steps2, 'gcode', fc.GcodeControls(printer_name=self.printer, initialization_data=self.setting))
        with open(filename, "w") as file:
            file.write(gcode)
        
        return gcode