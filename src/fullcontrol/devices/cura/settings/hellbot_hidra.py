default_initial_settings = {
    "name": "Hellbot Hidra",
    "manufacturer": "Hellbot",
    "start_gcode": "G21;\nG90;\nM82;\nM107;\nG28;\nG1 Z15.0 F9000;",
    "end_gcode": "M104 T0 S0;\nM104 T1 S0;\nM140 S0;\nG92 E1;\nG1 E-1 F300;\nG28 X0 Y0;\nM84;",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 120,
    "dia_feed": 2.85,
    "build_volume_x": 220,
    "build_volume_y": 220,
    "build_volume_z": 250,
}