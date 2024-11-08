default_initial_settings = {
    "name": "Eazao Zero",
    "manufacturer": "Eazao",
    "start_gcode": "G21 \nG90 ;absolute positioning\nM82 ;set extruder to absolute mode\nG28 ;Home \nG1 Z15.0 F1500 ;move the platform down 15mm\nG92 E0 \nG1 F300 E10\nG92 E0\nM302\nM163 S0 P0.9; Set Mix Factor\nM163 S1 P0.1; Set Mix Factor\nM164 S0\n",
    "end_gcode": "G92 E10\nG1 E-10 F300\nG28 X0 Y0 ;move X Y to min endstops\nM82\nM84 ;steppers off\n",
    "bed_temp": 60,
    "nozzle_temp": 0,
    "material_flow_percent": 100,
    "print_speed": 20.0,
    "travel_speed": 20.0,
    "dia_feed": 2.85,
    "build_volume_x": 150,
    "build_volume_y": 150,
    "build_volume_z": 240,
}
