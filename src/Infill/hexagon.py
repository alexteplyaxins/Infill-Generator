import math

class Hexagon:
    def __init__(self, density, ewidth, bounds, pos):
        self.density = density
        self.ewidth = ewidth
        self.bounds = bounds
        self.pos = pos

    def gen_hexagon_infill(self):
        if self.density <= 0.0:
            return []
        if self.density > 1.0:
            self.density = 1.0

        minx, miny, maxx, maxy = self.bounds

        # Calculate hexagon dimensions
        hex_height = 2 * self.ewidth / self.density
        hex_width = math.sqrt(3) * hex_height
        hex_half_height = hex_height / 2
        out = []

        # Adjust starting position using the x and y shifts
        start_x = minx + self.pos[0]
        start_y = miny + self.pos[1]

        n_rows = int((maxy - miny + 1.5 * hex_height) / (1.5 * hex_height))
        n_cols = int((maxx - minx + hex_width / 2) / hex_width)
        # n_rows = math.ceil((maxy - start_y) / hex_height / 2)
        # n_rows += int((start_y - miny) / hex_height / 2)
        # n_cols = math.ceil((maxx - start_x)/ hex_width)
        # n_cols += int((start_x - minx)/hex_width)

        # Generate hexagons row by row
        y = start_y - n_rows * hex_height / 2
        offset = 0
        for _ in range(-n_rows, n_rows):
            x = start_x - n_cols * hex_width / 2 + offset
            for _ in range(-n_cols, n_cols):
                # Generate hexagon line segments
                hexagon_points = [
                    (x, y),
                    (x + hex_width / 2, y - hex_half_height),
                    (x + hex_width, y),
                    (x + hex_width, y + hex_height),
                    (x + hex_width / 2, y + hex_height + hex_half_height),
                    (x, y + hex_height),
                    # (x, y)
                ]
                for i in range(len(hexagon_points) - 1):
                    line = [hexagon_points[i], hexagon_points[i + 1]]
                    # Clip the line if it exceeds the bounding box
                    clipped_line = self.clip_line_to_bounds(line, self.bounds)
                    if clipped_line:
                        out.append(clipped_line)
                x += hex_width
            # Adjust starting position for alternate rows
            offset = 0 if offset else -hex_width / 2
            y += 1.5 * hex_height

        return out

    def clip_line_to_bounds(self, line, bounds):
        # Implement the Cohen-Sutherland line-clipping algorithm
        # This algorithm clips a line from P1 = (x1, y1) to P2 = (x2, y2) against a rectangle with diagonal from (xmin, ymin) to (xmax, ymax)
        x1, y1 = line[0]
        x2, y2 = line[1]
        xmin, ymin, xmax, ymax = bounds

        INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

        def compute_outcode(x, y):
            code = INSIDE
            if x < xmin:
                code |= LEFT
            elif x > xmax:
                code |= RIGHT
            if y < ymin:
                code |= BOTTOM
            elif y > ymax:
                code |= TOP
            return code

        outcode1 = compute_outcode(x1, y1)
        outcode2 = compute_outcode(x2, y2)
        accept = False

        while True:
            if not (outcode1 | outcode2):
                accept = True
                break
            elif outcode1 & outcode2:
                break
            else:
                x, y = 0, 0
                outcode_out = outcode1 if outcode1 else outcode2

                if outcode_out & TOP:
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                    y = ymax
                elif outcode_out & BOTTOM:
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                    y = ymin
                elif outcode_out & RIGHT:
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                    x = xmax
                elif outcode_out & LEFT:
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                    x = xmin

                if outcode_out == outcode1:
                    x1, y1 = x, y
                    outcode1 = compute_outcode(x1, y1)
                else:
                    x2, y2 = x, y
                    outcode2 = compute_outcode(x2, y2)

        if accept:
            return [(x1, y1), (x2, y2)]
        else:
            return None