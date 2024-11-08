import math
import turtle
import matplotlib.pyplot as plt
import numpy as np

# Adjust this value for desired smoothness
CIRCLE_SMOOTH_FACTOR = 20
def interpolate_circle(start, end, segments=7, direction="cw"):
    # Compute the center of the semi-circle (midpoint of A and B)
    mid_pt = ((start[0] + end[0]) / 2., (start[1] + end[1]) / 2.)

    # Compute the radius
    radius = np.linalg.norm(np.array(start) - np.array(end)) / 2.

    # Compute the starting angle
    delta_x = end[0] - start[0]
    delta_y = end[1] - start[1]
    theta = np.arctan2(delta_y, delta_x)

    # Generate points on the semi-circle based on direction
    if direction == "ccw":
        angles = np.linspace(theta, theta + np.pi, segments)
    elif direction == "cw":
        angles = np.linspace(theta, theta - np.pi, segments)
    else:
        raise ValueError("Direction should be either 'cw' or 'ccw'")

    # Generate the x, y coordinates
    x = np.round(mid_pt[0] + radius * np.cos(angles), 2)
    x = x[::-1]
    y = np.round(mid_pt[1] + radius * np.sin(angles), 2)
    y = y[::-1]

    prev_pt = (x[0], y[0])
    inter_lines = []
    for i in range(1, len(x)):
        new_pt = (x[i], y[i])
        line = [prev_pt, new_pt]
        prev_pt = new_pt
        # interpolated_points.append((x, y))
        inter_lines.append(line)
    return inter_lines


class Circle:
    def __init__(self, rect, density, distance=4, base_angle=0, pos=[0, 0], ewidth=0.4):
        if density <= 0.0:
            return []
        if density > 1.0:
            density = 1.0

        self.density = density
        self.ewidth = ewidth
        self.pos = pos
        self.rect = rect
        self.radius = ewidth / density
        self.spacing = ewidth / density
        # if distance < self.radius:
        #     self.spacing = self.radius
        # else:
        #     self.spacing = distance

        self.layer1_lines = []
        self.layer2_lines = []
        self.base_angle = base_angle

    def _make_infill_pat(self, rot, layer_lines):
        shift_x, shift_y = self.pos
        min_x, min_y, max_x, max_y = self.rect
        w = max_x - min_x
        h = max_y - min_y
        cx = math.floor((max_x + min_x) / 2.0 / self.spacing) * self.spacing + shift_x
        cy = math.floor((max_y + min_y) / 2.0 / self.spacing) * self.spacing + shift_y
        r = max(w, h) * 2 + max(abs(shift_x), abs(shift_y))  # Extend more based on the shifts
        c1 = math.cos((self.base_angle + rot) * math.pi / 180.0)
        s1 = math.sin((self.base_angle + rot) * math.pi / 180.0)
        c2 = math.cos((self.base_angle + rot + 90) * math.pi / 180.0) * self.spacing
        s2 = math.sin((self.base_angle + rot + 90) * math.pi / 180.0) * self.spacing
        for i in range(1 - int(r / self.spacing), int(r / self.spacing)):
            cp = (cx + c2 * i, cy + s2 * i)
            line = [
                (cp[0] + r * c1, cp[1] + r * s1),
                (cp[0] - r * c1, cp[1] - r * s1)
            ]
            split_line = self.split_smaller_lines(line[0], line[1])
            layer_lines += split_line

    def generate_layer1_lines(self):
        self._make_infill_pat(rot=0, layer_lines=self.layer1_lines)
        return self.layer1_lines

    def generate_layer2_lines(self):
        self._make_infill_pat(rot=90, layer_lines=self.layer2_lines)
        return self.layer2_lines

    def split_smaller_lines(self, start_pt, end_pt):
        num_of_space = math.ceil(np.linalg.norm(np.array(start_pt) - np.array(end_pt))/self.radius/2)
        x = np.linspace(start_pt[0], end_pt[0], num_of_space)
        y = np.linspace(start_pt[1], end_pt[1], num_of_space)

        split_lines = []
        prev_pt = (x[0], y[0])
        rev = False
        for idx in range(1, len(x)):
            curr_pt = (x[idx], y[idx])
            if rev is False:
                cw_lines = interpolate_circle(prev_pt, curr_pt, direction='cw')
                split_lines += cw_lines
            else:
                ccw_lines = interpolate_circle(prev_pt, curr_pt, direction='ccw')
                split_lines += ccw_lines
            rev = not rev
            prev_pt = curr_pt
        return split_lines


def visualize_lines(lines):
    fig, ax = plt.subplots()

    for line in lines:
        ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'b-')

    ax.set_aspect('equal', 'box')
    plt.show()


def visualize_with_turtle(lines):
    # Setup the turtle
    t = turtle.Turtle()
    t.speed('slowest')  # Slowest speed for visualization
    screen = turtle.Screen()

    # Compute bounds of the data
    min_x = min([min(line[0][0], line[1][0]) for line in lines]) - 5
    max_x = max([max(line[0][0], line[1][0]) for line in lines]) + 5
    min_y = min([min(line[0][1], line[1][1]) for line in lines]) - 5
    max_y = max([max(line[0][1], line[1][1]) for line in lines]) + 5

    # Set the world coordinates to fit the data
    screen.setworldcoordinates(min_x, min_y, max_x, max_y)

    # Move the turtle to the starting point of the first line without drawing
    t.penup()
    t.goto(lines[0][0])
    t.pendown()

    # Draw each line in the list
    for line in lines:
        start, end = line
        t.goto(start)
        t.goto(end)

    turtle.done()

if __name__=='__main__':
    rect = [89.781, 70.539, 124.522, 125.393]
    distance = 1.0
    c = Circle(rect=rect, density=0.8, segments=100)
    lines = c.generate_layer1_lines()
    # visualize_with_turtle(lines)

    # lines = c.generate_layer2_lines()
    # c.visualize(lines)
    visualize_with_turtle(lines)