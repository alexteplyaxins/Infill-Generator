default_initial_settings = {
    "name": "Cremaker S V1",
    "manufacturer": "JOYPLACE CO., LTD.",
    "start_gcode": "G28\nG1 Z5.0 F6000\nG1 X2 Y5 F3000\nG1 Z0.3\nG92 E0\nG1 Y100 E10 F600\nG92 E0",
    "end_gcode": "M104 S0 ; turn off extruder\nM140 S0 ; turn off heatbed\nG92 E1\nG1 E-1 F300\nG28 X0 Y180\nM84",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 100,
    "dia_feed": 1.75,
    "build_volume_x": 200,
    "build_volume_y": 200,
    "build_volume_z": 160,
}