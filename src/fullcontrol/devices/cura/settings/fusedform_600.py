default_initial_settings = {
    "name": "FF600",
    "manufacturer": "Fused Form",
    "start_gcode": "G21 ;metric values\nG90 ;absolute positioning\nM82 ;set extruder to absolute mode\nM107 ;start with the fan off\nG28 X0 Y0 ;move X/Y to min endstops\nG28 Z0 ;move Z to min endstops\nG1 Z15.0 F9000 ;move the platform down 15mm\nG92 E0 ;zero the extruded length\nG1 F200 E6 ;extrude 6 mm of feed stock\nG92 E0 ;zero the extruded length again\n;Put printing message on LCD screen\nM117 Printing...",
    "end_gcode": "M104 S0 ;extruder heater off\nM140 S0 ;heated bed heater off\nG91 ;relative positioning\nG1 E-1 F300  ;retract the filament a bit before lifting the nozzle, to release some of the pressure\nG28 X0 Y0 ;move X/Y to min endstops, so the head is out of the way\nM84 ;steppers off\nG90 ;absolute positioning\nM107 ; Fans off",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 45,
    "travel_speed": 75,
    "dia_feed": 2.85,
    "build_volume_x": 500,
    "build_volume_y": 500,
    "build_volume_z": 600,
}
