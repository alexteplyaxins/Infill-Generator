default_initial_settings = {
    "name": "Maker Pegasus",
    "manufacturer": "Maker",
    "start_gcode": "G1 Z15;\nG28;Home\nG29;Auto Level\nG1 Z5 F5000;Move the platform down 15mm",
    "end_gcode": "M104 S0;Turn off temperature\nG28 X0; Home X\nM84; Disable Motors",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 120,
    "dia_feed": 2.85,
    "build_volume_x": 400,
    "build_volume_y": 400,
    "build_volume_z": 400,
}
