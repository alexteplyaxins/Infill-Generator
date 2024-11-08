from model.grid1 import GridInfill
from model.primitives import Cell

class InfillGenerator:

    def __init__(self, model):
        self.bounds = []
        self.pos = [0, 0]
        self.layer = 0
        self.model = model
        
    def generate_infill(self, bounds, cyc_index):
        self.bounds = bounds
        lines = self.make_infill_pat(self.bounds, cyc_index)
        return lines
    
    def make_infill_pat(self, rect, cyc_index):
        """
        
        """
        min_x, min_y, max_x, max_y = rect
        shift_x, shift_y = self.pos
        width = max_x - min_x
        height = max_y - min_y
        shift_x, shift_y = -width/2, -height/2

        grid = GridInfill(cell = self.cell, scale = self.scale,
                          width =  width, height = height, 
                          shiftx=shift_x, shifty=shift_y, cyc_index=cyc_index)
        
        return grid.get_grid()
    
   
    def _line_intersection(self, p1, p2, mask):
        """ Return the intersection point of two line segments (p1,p2) and (p3,p4) """
        s1_x = p2[0] - p1[0]
        s1_y = p2[1] - p1[1]
        n = len(mask)
        for i in range(0, n):
            p3 = mask[i]
            p4 = mask[(i+1)%n]
            s2_x = p4[0] - p3[0]
            s2_y = p4[1] - p3[1]

            s = (-s1_y * (p1[0] - p3[0]) + s1_x * (p1[1] - p3[1])) / (-s2_x * s1_y + s1_x * s2_y)
            t = (s2_x * (p1[1] - p3[1]) - s2_y * (p1[0] - p3[0])) / (-s2_x * s1_y + s1_x * s2_y)

            if 0 <= s <= 1 and 0 <= t <= 1:
                # Collision detected
                intersection_x = p1[0] + (t * s1_x)
                intersection_y = p1[1] + (t * s1_y)
                return (intersection_x, intersection_y)
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
        # Check all segments of path1 against all segments of path2
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

    