default_initial_settings = {
    "name": "Rigid3D Zero2",
    "manufacturer": "Rigid3D",
    "start_gcode": "; -- START GCODE --\nG21 ; mm olculer\nG28 ; Eksenleri sifirla\nM420 S1 ; Yazilim destekli tabla seviyeleme\nM107 ; Fani kapat\nG90 ; Mutlak konumlama\nG1 Z5 F180 ; Z eksenini 5mm yukselt\nG1 X30 Y30 F3000 ; Konuma git\nM82 ; Ekstruder mutlak mod\nG92 E0 ; Ekstruder konumu sifirla\n; -- end of START GCODE --",
    "end_gcode": "; -- END GCODE --\nG1 X0 Y180 ; Konuma git\nM107 ; Fani kapat\nG91 ; Goreceli konumlama\nG0 Z20 ; Tablayi alcalt\nT0\nG1 E-2 ; Filaman basincini dusur\nM104 T0 S0 ; Ekstruder isiticiyi kapat\nG90 ; Mutlak konumlama\nG92 E0 ; Ekstruder konumu sifirla\nM140 S0 ; Tabla isiticiyi kapat\nM84 ; Motorlari durdur\nM300 S2093 P150 ; Baski sonu melodisi\nM300 S2637 P150\nM300 S3135 P150\nM300 S4186 P150\nM300 S3135 P150\nM300 S2637 P150\nM300 S2793 P150\nM300 S2349 P150\nM300 S1975 P150\nM300 S2093 P450\n; -- end of END GCODE --\n",
    "bed_temp": 60,
    "nozzle_temp": 210,
    "material_flow_percent": 100,
    "print_speed": 60,
    "travel_speed": 80.0,
    "dia_feed": 1.75,
    "build_volume_x": 200,
    "build_volume_y": 200,
    "build_volume_z": 192,
}
