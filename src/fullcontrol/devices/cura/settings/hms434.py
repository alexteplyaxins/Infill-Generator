default_initial_settings = {
    "name": "HMS434",
    "manufacturer": "Hybrid AM Systems",
    "start_gcode": "\n;Neither Hybrid AM Systems nor any of Hybrid AM Systems representatives has any liabilities or gives any warranties on this .gcode file, or on any or all objects made with this .gcode file.\n\nM114\n\nM140 S{data['bed_temp']}\nM118 // action:chamber_fan_on\nM141 S{0}\n\nM117 Homing Y ......\nG28 Y\nM117 Homing X ......\nG28 X\nM117 Homing Z ......\nG28 Z F100\n\nG1 Z10 F900\nG1 X-25 Y20 F12000\n\nM190 S{data['bed_temp']}\n\nM117 HMS434 Printing ...",
    "end_gcode": "",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 50,
    "travel_speed": 250,
    "dia_feed": 1.75,
    "build_volume_x": 450,
    "build_volume_y": 325,
    "build_volume_z": 400,
}
