default_initial_settings = {
    "name": "Dagoma Sigma",
    "manufacturer": "Dagoma",
    "start_gcode": ";Author: Dagoma\n\n\n\nG90 ;absolute positioning\nM104 S120 ;Launch heating up to 120°C\nM106 S255 ;Activating layers fans\nG29 ;Homing and Calibration\nM107 ;Off Ventilateur\nM109 S{data['nozzle_temp']} U-55 X55 V-85 Y-85 W0.26 Z0.26 ;Temperature for the first layer only\nM82 ;Set extruder to absolute mode\nG92 E0 ;Zero the extruded length\nG1 F200 E6 ;Extrude 10mm of feed stock\nG92 E0 ;Zero the extruded length again\nG1 F200 E-3.5\nG0 Z0.15\nG0 X10\nG0 Z3\nG1 F{data['travel_speed']}\nM117 Printing...\n",
    "end_gcode": ";Author: Dagoma\n\nM104 S0\nM107\nM140 S0\nG91\nG1 E-1 F300\nG1 Z+3 E-2 F9000\nG90\nG28\n",
    "bed_temp": 60,
    "nozzle_temp": 205,
    "material_flow_percent": 100,
    "print_speed": 40,
    "travel_speed": 150,
    "dia_feed": 2.85,
    "build_volume_x": 195.55,
    "build_volume_y": 195.55,
    "build_volume_z": 205,
}
