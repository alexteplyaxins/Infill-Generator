default_initial_settings = {
    "name": "Two Trees Base Printer",
    "manufacturer": "Two Trees",
    "start_gcode": "G28 ;Home\nM420 S1 ;Enable ABL using saved Mesh and Fade Height\nG92 E0 ;Reset Extruder\nG1 Z2.0 F3000 ;Move bed down\nG1 X10.1 Y20 Z0.28 F5000.0 ;Move to start position\nG1 X10.1 Y200.0 Z0.28 F1500.0 E15 ;Draw the first line\nG1 X10.4 Y200.0 Z0.28 F5000.0 ;Move to side a little\nG1 X10.4 Y20 Z0.28 F1500.0 E30 ;Draw the second line\nG92 E0 ;Reset Extruder\nG1 Z2.0 F3000 ;Move Bed up",
    "end_gcode": "G91 ;Relative positioning\nG1 E-2 F2700 ;Retract a bit\nG1 E-2 Z0.2 F2400 ;Retract and raise Z\nG1 X5 Y5 F3000 ;Wipe out\nG1 Z10 ;Raise Z more\nG90 ;Absolute positioning\n\nG1 X0 Y{data['build_volume_y']} ;Present print\nM106 S0 ;Turn-off fan\nM104 S0 ;Turn-off hotend\nM140 S0 ;Turn-off bed\n\nM84 X Y E ;Disable all steppers but Z\n",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 50.0,
    "travel_speed": 120,
    "dia_feed": 1.75,
    "build_volume_x": 100,
    "build_volume_y": 100,
    "build_volume_z": 100,
}
