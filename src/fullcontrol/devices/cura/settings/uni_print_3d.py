default_initial_settings = {
    "name": "Uni-Print-3D",
    "manufacturer": "TheCoolTool",
    "start_gcode": "M53; enable feed-hold\nG0 Z2.0; always start from the same height to compensate backlash\nG28; move extruder to 0\nM420 R0.0 E0.0 D0.0 P0.1 ; turn the lights on\nM107; turn off fan\nG64 P0.05 Q0.05; path blending settings\nG23; unretract",
    "end_gcode": "M104 P0 ; turn off hotend\nG0 X-80 Y100; move the extruder out of the way\nM420 R0.0 E0.1 D0.0 P0.6 ; signalize end of print\nM140 P0 ; turn off heatbed\nM65 P16 ; turn off external fan\nM65 P15 ; turn off power",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 120,
    "dia_feed": 2.85,
    "build_volume_x": 186,
    "build_volume_y": 220,
    "build_volume_z": 230,
}
