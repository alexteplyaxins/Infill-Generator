default_initial_settings = {
    "name": "Blocks One MKII",
    "manufacturer": "Blocks",
    "start_gcode": "G21\nG90 ;absolute positioning\nM82 ;set extruder to absolute mode\nM107 ;start with the fan off\nG28 X0 Y0  ;move X/Y to min endstops\nG28 Z0 ;move Z to min endstops\nG29\nG1 X-14 Y0 F6000\nG1 Z0.1\nG92 E0 ;zero the extruded length\nG1 F2000 E10 ;extrude 10mm of feed stock\nG92 E0 ;zero the extruded length again\nG1 Z0.2 F6000\nG1 F6000\nM117 Printing...\n",
    "end_gcode": "M104 S0 ;extruder heater off\nM140 S0 ;heated bed heater off (if you have it)\nG91 ;relative positioning\nG1 E-1 F300 ;retract the filament a bit before lifting the nozzle, to release some of the pressure\nG1 Z+0.5 E-5 X-20 Y-20 F6000 ;move Z up a bit and retract filament even more\nG28 X0 Y0 ;move X/Y to min endstops, so the head is out of the way\nM84 ;steppers off\nG90 ;absolute positioning\n",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 150.0,
    "dia_feed": 1.75,
    "build_volume_x": 200,
    "build_volume_y": 210,
    "build_volume_z": 210,
}
