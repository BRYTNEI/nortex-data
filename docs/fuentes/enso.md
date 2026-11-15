# ENSO: ICEN y ONI

| Campo | Valor |
| :-- | :-- |
| Endpoint | `http://met.igp.gob.pe/datos/ICEN.txt` (ICEN oficial, ENFEN 2024) y `https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt` (ONI) |
| Autenticación | Ninguna |
| Variables | `icen`, `oni` (anomalía, °C) |
| Resolución | Índices regionales mensuales (Niño 1+2 y Niño 3.4) |
| Ventana aplicada | Todo el registro desde 1950: la v0.7 los usa para clasificar años y elegir análogos (§6.3) |
| Rango real obtenido | 1950-01 → 2026-09 (921 meses). ICEN sep-2026 = +4,50; ONI ASO-2026 = +2,46; ICEN 2023 máx. +2,92 |
| Decisiones que alimenta | Estratificación de escenarios, etiqueta de campaña (RF-27), riesgo de invierno cálido en mango |
| Limitación | La clasificación en El Niño / La Niña Costera según ENFEN se hará en el motor; aquí solo se publica el índice |
