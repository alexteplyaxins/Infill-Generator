default_initial_settings = {
    "name": "Koonovo Base Printer",
    "manufacturer": "Koonovo",
    "start_gcode": "G21 ;metric values\nG90 ;absolute positioning\nM82 ;set extruder to absolute mode\nM107 ;start with the fan off\nG28 ;Move to min endstops\nG1 Z15.0 F9000 ;move the platform down 15mm\nM117 Printing...",
    "end_gcode": "M104 T0 S0 ;1st extruder heater off\nM104 T1 S0 ;2nd extruder heater off\nM140 S0 ;heated bed heater off (if you have it)\nG91 ;relative positioning\nG1 E-1 F300  ;retract the filament a bit before lifting the nozzle, to release some of the pressure\nG1 Z+0.5 E-5 X-20 Y-20 F9000 ;move Z up a bit and retract filament even more\nG28 X0 Y0 ;move X/Y to min endstops, so the head is out of the way\nM84 ;steppers off\nG90 ;absolute positioning",
    "bed_temp": 55,
    "nozzle_temp": 195,
    "material_flow_percent": 100,
    "print_speed": 50.0,
    "travel_speed": 120.0,
    "dia_feed": 1.75,
    "build_volume_x": 100,
    "build_volume_y": 100,
    "build_volume_z": 100,
}
