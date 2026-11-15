# SoilGrids 2.0 (ISRIC)

| Campo | Valor |
| :-- | :-- |
| Endpoint | WCS `https://maps.isric.org/mapserv` (`GetCoverage` con ventana de ±0,01°) |
| Autenticación | Ninguna |
| Variables | `soil_clay`, `soil_sand`, `soil_silt` (%), `soil_soc` (g/kg), `soil_ph`, `soil_bdod` (kg/dm³), `soil_cec` (cmol(c)/kg), `soil_theta_fc` y `soil_theta_wp` (m³/m³) en 5 profundidades (0–100 cm) |
| Resolución | 250 m, estático |
| Rango real obtenido | Punto piloto: franco arenoso (≈ 60 % arena, 14 % arcilla); θ_FC ≈ 0,28 y θ_WP ≈ 0,12 m³/m³. Píxel válido más cercano a 0,7–1,0 km: el resto de la ventana está enmascarado por SoilGrids |
| Decisiones que alimenta | TAW/RAW del balance (§9.3) y autonomía entre turnos (§9.5) cuando no hay laboratorio (EX-03) |
| Problemas | La API REST respondió HTTP 503 y el servidor de archivos rechazó conexiones el 15/11/2026; el WCS sí respondió |
| Limitación | Dato global, no de la parcela: el análisis de laboratorio (`plantillas/suelo_laboratorio.csv`) siempre tiene prioridad. La retención de agua de SoilGrids suele ser alta para suelos arenosos: contrastar con laboratorio |
