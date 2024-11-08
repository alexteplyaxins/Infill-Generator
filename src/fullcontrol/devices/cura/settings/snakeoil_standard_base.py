default_initial_settings = {
    "name": "SnakeOil Standard Base",
    "manufacturer": "SnakeOilXY",
    "start_gcode": ";Simple\nSTART_PRINT EXTRUDER_TEMP={data['nozzle_temp']} BED_TEMP={data['bed_temp']}\n;Or with custom bed mesh area",
    "end_gcode": "END_PRINT",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 300,
    "dia_feed": 1.75,
    "build_volume_x": 165,
    "build_volume_y": 165,
    "build_volume_z": 165,
}
