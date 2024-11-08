default_initial_settings = {
    "name": "HCTECH_HC300-M3",
    "manufacturer": "HCTECH",
    "start_gcode": "G28 X Y ;Home XY\nG92 E0 ;Reset Extruder\nG1 E-1 F2400 ;Retract\nG92 E0 ;Reset Extruder\nG28 Z ;home Z\nG29 ; Measure the bed\nM500 ; Store to EEPROM\nG1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed\nG1 X0.1 Y20 Z0.36 F5000.0 ; Move to start position\nG1 X0.1 Y200.0 Z0.36 F1500.0 E15 ; Draw the first line\nG1 X0.4 Y200.0 Z0.36 F5000.0 ; Move to side a little\nG1 X0.4 Y20 Z0.36 F1500.0 E30 ; Draw the second line\nG92 E0 ; Reset Extruder",
    "end_gcode": "G91 ;Relative positioning\nG1 E-2 F2700 ;Retract a bit\nG1 Z1 E-2 F2400 ;Retract and raise Z\nG1 Z2 ;Raise Z\nG90 ;Absolute positioning\nG1 X5 Y290 ;Return to Start Point\nM106 S0 ;Switch off part cooling fan\nM104 S0 ;turn off temperature\nM140 S0 ;turn off Heated Bed\nM84 X Y E ;Disable all steppers but Z",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60.0,
    "travel_speed": 120,
    "dia_feed": 1.75,
    "build_volume_x": 300,
    "build_volume_y": 300,
    "build_volume_z": 300,
}
