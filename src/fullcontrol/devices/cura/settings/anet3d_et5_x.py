default_initial_settings = {
    "name": "Anet ET5 X",
    "manufacturer": "Anet",
    "start_gcode": "G28 ;Home\nG1 Z15.0 F2000 ;Move the platform",
    "end_gcode": "M104 S0\nM140 S0\nG92 E0\nG1 E-10 F2000\nG28 X0 Y0\nM84",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 50.0,
    "travel_speed": 150.0,
    "dia_feed": 1.75,
    "build_volume_x": 300,
    "build_volume_y": 300,
    "build_volume_z": 400,
}
