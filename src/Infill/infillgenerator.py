import math
from Infill.honeycomb_tri import HoneyCombTri
from Infill.circle_tri import Circle
from Infill.hexagon import Hexagon
import numpy as np
from model.primitives import Cell, InfillGraph 
class InfillGenerator:

    def __init__(self):
        self.infill_type = ''
        self.bounds = []
        self.pos = [0, 0]
        self.base_angle = 0
        self.ewidth = 0.4
        self.density = 0
        self.layer = 0
        self.cell = Cell(r"./DXF files/honeycomb.DXF")\
        
    def generate_infill(self, density, spacing, infill_type, bounds, ewidth, layer_num, pos):
        self.pos = pos
        self.density = density
        self.spacing = spacing
        self.bounds = bounds
        self.ewidth = ewidth
        if infill_type == "Lines":
            self.base_angle = 90 * (layer_num % 2) + 45
            lines = self.gen_lines_infill()
        elif infill_type == "Lines-0":
            self.base_angle = 0
            lines = self.gen_lines_infill()
        elif infill_type == "Lines-90":
            self.base_angle = 90
            lines = self.gen_lines_infill()      
        elif infill_type == "Lines-0-90":
            self.base_angle = 90 * (layer_num % 2)
            lines = self.gen_lines_infill()
        elif infill_type == "Lines-0-45-90-135":
            self.base_angle = 45 * (layer_num % 4)
            lines = self.gen_lines_infill()
        elif infill_type == "Triangles":
            self.base_angle = 60 * (layer_num % 3)
            lines = self.gen_triangle_infill()
        elif infill_type == "Grid":
            self.base_angle = 90 * (layer_num % 2) + 45
            lines = self.gen_grid_infill()
        elif infill_type == "Hexagons":
            self.base_angle = 0
            lines = self.gen_hexagon_infill()
        elif infill_type == "Honeycomb":
            self.base_angle = 0
            self.layer = layer_num
            if layer_num % 3 == 0:
                self.bounds = bounds
            lines = self.gen_honeycomb_infill()
        elif infill_type == "Circle":
            self.base_angle = 0
            self.layer = layer_num
            if layer_num % 2 == 0:
                self.bounds = bounds
            lines = self.gen_circle_infill()
        else:
            lines = []

        return lines
    
    def make_infill_pat3(self, rect, baseang, spacing, rots):
        min_x, min_y, max_x, max_y = rect
        w = max_x - min_x
        h = max_y - min_y
        nx = math.ceil(w/spacing)
        ny = math.ceil  (h/spacing)

        graph = InfillGraph(self.cell, ny, nx)
        lines = graph.find_cycles()
        return lines

    def make_infill_pat2(self, rect, baseang, spacing, rots):
        """
        
        """
        min_x, min_y, max_x, max_y = rect
        shift_x, shift_y = self.pos
        w = max_x - min_x
        h = max_y - min_y
        cx = math.floor((max_x + min_x) / 2.0 / spacing) * spacing + shift_x
        cy = math.floor((max_y + min_y) / 2.0 / spacing) * spacing + shift_y
        r = max(w, h) * 2 + max(abs(shift_x), abs(shift_y))  # Extend more based on the shifts
        out = []
        
        # graph1 = InfillGraph(self.cell, 2, 2)
        # graph1.combine_cycle(2)
        # lines = graph1.get_infill_paths(index=0)
        # return lines
    
        for rot in rots:
            c1 = math.cos((baseang + rot) * math.pi / 180.0)
            s1 = math.sin((baseang + rot) * math.pi / 180.0)
            c2 = math.cos((baseang + rot + 90) * math.pi / 180.0) * spacing
            s2 = math.sin((baseang + rot + 90) * math.pi / 180.0) * spacing
            for i in range(1 - int(r / spacing), int(r / spacing)):
                cp = (cx + c2 * i, cy + s2 * i)
                line = [
                    (cp[0] + r * c1, cp[1] + r * s1),
                    (cp[0] - r * c1, cp[1] - r * s1)
                ]
                # clipped_line = self.clip_line_to_rect(line[0], line[1], rect)
                out.append(line)
               # print(line)
        return out

    def make_infill_pat(self, rect, baseang, spacing, rots):
        """
        Generate infill patterns (lines) within a specified rectangle based on given angles and spacing.

        Parameters:
        - rect (list): A bounding rectangle specified as (minx, miny, maxx, maxy).
        - baseang (float): The base angle for the infill lines in degrees.
        - spacing (float): The distance between infill lines.
        - rots (list of floats): A list of angles to rotate the base infill pattern.

        Returns:
        - list of list of tuples: A list of infill paths.
        """
        min_x, min_y, max_x, max_y = rect
        w = max_x - min_x
        h = max_y - min_y
        cx = math.floor((max_x + min_x) / 2.0 / spacing) * spacing
        cy = math.floor((max_y + min_y) / 2.0 / spacing) * spacing
        r = math.hypot(w, h) / math.sqrt(2)
        n = int(math.ceil(r / spacing))
        out = []
        for rot in rots:
            c1 = math.cos((baseang + rot) * math.pi / 180.0)
            s1 = math.sin((baseang + rot) * math.pi / 180.0)
            c2 = math.cos((baseang + rot + 90) * math.pi / 180.0) * spacing
            s2 = math.sin((baseang + rot + 90) * math.pi / 180.0) * spacing
            for i in range(1 - n, n):
                cp = (cx + c2 * i, cy + s2 * i)
                line = [
                    (cp[0] + r * c1 , cp[1] + r * s1),
                    (cp[0] - r * c1, cp[1] - r * s1)
                ]
                out.append(line)
        return out


    def __gen_lines_pat3(self, rot, spacing):
        minx, miny, maxx, maxy = self.bounds
        shift_x = self.pos[0]
        shift_y = self.pos[1]
        lines = []

        # Tính khoảng cách giữa hai đường thẳng đứng
        vertical_distance = 2 * (maxy - miny)

        # Góc nghiêng 135 độ (đổi sang radian)
        angle = np.radians(rot)

        # Tính toán số lượng đường nghiêng cần vẽ
        num_lines = int((2 * vertical_distance) / spacing)
        # Tạo danh sách các đường nghiêng 135 độ
        for i in range(num_lines + 1):
            y_intercept = i * spacing - vertical_distance / 2 + shift_y
            x_start = minx + shift_x
            x_end = maxx + shift_x
            y_start = y_intercept
            y_end = y_intercept - (x_end - x_start) * np.tan(angle)
            lines.append([(x_start, y_start), (x_end, y_end)])
        return lines

    # 0-45-90-135
    def __gen_lines_infill_0(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = self.ewidth / self.density
        return self.__gen_lines_pat3(0, spacing)

    def __gen_lines_infill_45(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = self.ewidth / self.density
        return self.__gen_lines_pat3(45, spacing)

    def __gen_lines_infill_90(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = self.ewidth / self.density
        minx, miny, maxx, maxy = self.bounds
        shift_x = self.pos[0]
        shift_y = self.pos[1]
        lines = []
        # Tính toán số lượng đường thẳng song song cần vẽ
        num_lines = int((2 * maxx - minx) / spacing)

        # Tạo danh sách các đường thẳng song song theo phương thẳng đứng
        for i in range(num_lines + 1):
            x_intercept = minx + i * spacing + shift_x
            lines.append([(x_intercept, maxy + shift_y), (x_intercept, -miny + shift_y)])
        return lines

    def __gen_lines_infill_135(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = self.ewidth / self.density
        return self.__gen_lines_pat3(135, spacing)

    def gen_lines_infill(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = self.ewidth / self.density
        return self.make_infill_pat2(self.bounds, self.base_angle, spacing, rots=[0])

    def gen_triangle_infill(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = 3.0 * self.ewidth / self.density
        return self.make_infill_pat2(self.bounds, self.base_angle, spacing, [0, 60, 120])

    def gen_grid_infill(self):
        if self.spacing > 0:
            spacing = self.spacing
        else:   
            if self.density <= 0.0:
                return []
            if self.density > 1.0:
                self.density = 1.0
            spacing = 2.0 * self.ewidth / self.density
        return self.make_infill_pat2(self.bounds, self.base_angle, spacing, [0, 90])

    def gen_hexagon_infill(self):
        if self.density <= 0.0:
            return []
        if self.density > 1.0:
            self.density = 1.0
        hexagon = Hexagon(bounds=self.bounds, ewidth=self.ewidth, density=self.density, pos=self.pos)
        return hexagon.gen_hexagon_infill()

    def init_honey_comb(self):
        self.hc = HoneyCombTri(rect=self.bounds, pos=self.pos, angle=self.base_angle,
                               ewidth=self.ewidth, density=self.density)

    def init_circle(self):
        self.ci = Circle(rect=self.bounds, pos=self.pos,
                         base_angle=self.base_angle, ewidth=self.ewidth, density=self.density)

    def gen_circle_infill(self):
        if self.layer % 2 == 0:
            self.init_circle()
            lines = self.ci.generate_layer1_lines()
        else:
            lines = self.ci.generate_layer2_lines()
        return lines

    def gen_honeycomb_infill(self):
        if self.layer % 3 == 0:
            self.init_honey_comb()
            lines = self.hc.generate_layer_1()
        elif self.layer % 3 == 1:
            lines = self.hc.generate_layer_2()
        else:
            lines = self.hc.generate_layer_3()
        return lines
