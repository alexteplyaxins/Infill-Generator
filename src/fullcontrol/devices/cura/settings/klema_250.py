default_initial_settings = {
    "name": "KLEMA 250",
    "manufacturer": "KLEMA",
    "start_gcode": "M140 S{data['bed_temp']} ;\nM190 S{data['bed_temp']} ;\nM501 ;\nM104 S150 ;\nG28 ;\nG90 ;\nG0 X0 Y0 F6000 ;\nM109 S{data['nozzle_temp']} ;\nG0 Z0.3 F300 ;\nG92 E0 ;\nG1 X70 E10 F500 ;\nG92 E0 ;\nG1 E-1 F500 ;\nG92 E0 ;\nG1 Z1 ;\nG1 X100 F6000 ;\nG1 E-1 F500 ;\nG92 E0",
    "end_gcode": "M104 S0 ;\nM140 S0 ;\nM107 ;\nG91 ;\nG1 E-1 F300 ;\nG1 Z+65 E-2 X-20 Y-20 F2000 ;\nG28 X0 Y0 ;\nG90",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 120,
    "dia_feed": 2.85,
    "build_volume_x": 250,
    "build_volume_y": 250,
    "build_volume_z": 350,
}
