
import os
from fullcontrol.gcode.point import Point
from fullcontrol.gcode.printer import Printer
from fullcontrol.gcode.extrusion_classes import ExtrusionGeometry, Extruder
from fullcontrol.gcode.state import State
from fullcontrol.gcode.controls import GcodeControls
from datetime import datetime
from fullcontrol.gcode.tips import tips


def footGcode():
    fGcode = []
    fGcode.append("G91 ;Relative positioning")
    fGcode.append("G1 E-2 F2700 ;Retract a bit")
    fGcode.append("G1 E-2 Z0.2 F2400 ;Retract and raise Z")
    fGcode.append("G1 X5 Y5 F3000 ;Wipe out")
    fGcode.append("G1 Z10 ;Raise Z more")
    fGcode.append("G90 ;Absolute positioning")
    fGcode.append("G1 X0 Y235 ;Present print")
    fGcode.append("M106 S0 ;Turn-off fan")
    fGcode.append("M104 S0 ;Turn-off hotend")
    fGcode.append("M140 S0 ;Turn-off bed")
    fGcode.append("M84 X Y E ;Disable all steppers but Z")
    fGcode.append("M82 ;absolute extrusion mode")
    fGcode.append("M104 S0")
    return (fGcode)
def headGcode():
    hGcode = []
    hGcode.append("G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position")
    hGcode.append("G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line")
    hGcode.append("G1 X0.4 Y200.0 Z0.3 F5000.0 ; Move to side a little")
    hGcode.append("G1 X0.4 Y20 Z0.3 F1500.0 E30 ; Draw the second line")
    return (hGcode)

def gcode(steps: list, gcode_controls: GcodeControls, show_tips: bool):
    '''
    Generate a gcode string from a list of steps.

    Args:
        steps (list): A list of step objects.
        gcode_controls (GcodeControls, optional): An instance of GcodeControls class. Defaults to GcodeControls().

    Returns:
        str: The generated gcode string.
    '''
    gcode_controls.initialize()
    if show_tips: tips(gcode_controls)

    state = State(steps, gcode_controls)
    # need a while loop because some classes may change the length of state.steps
    while state.i < len(state.steps):
        # call the gcode function of each class instance in 'steps'
        gcode_line = state.steps[state.i].gcode(state)
        if gcode_line != None:
            state.gcode.append(gcode_line)
        state.i += 1

        if state.i == 7: #Bo sung tam headcode vào vị trí số 7 (ko rõ ở đâu có index này)
            for code in headGcode():
                state.gcode.append(code)

    for code in footGcode():
        state.gcode.append(code)
    
    gc = '\n'.join(state.gcode)

    if gcode_controls.save_as != None:
        filename = gcode_controls.save_as
        filename += datetime.now().strftime("__%d-%m-%Y__%H-%M-%S.gcode") if gcode_controls.include_date == True else '.gcode'
        open(filename, 'w').write(gc)

    return gc
