# Estación de referencia (NOAA GSOD)

| Campo | Valor |
| :-- | :-- |
| Endpoint | `https://www.ncei.noaa.gov/access/services/data/v1` (`global-summary-of-the-day`, estación 84401099999) |
| Autenticación | Ninguna |
| Variables | `station_tmax`, `station_tmin`, `station_tmean`, `station_dewpoint`, `station_precip`, `station_wind` |
| Resolución | Puntual; aeropuerto de Piura, a ~33 km del punto piloto. Las filas llevan las coordenadas de la estación |
| Ventana aplicada | máx(1973-01-01, hoy − 10 años), bloques anuales con caché |
| Decisiones que alimenta | Validación y sesgo de POWER/IMERG (§19), sesgo de mínimas para noches frescas (§9.6) |
| Problemas resueltos | Los días sin reporte de lluvia (atributo `I`) llegaban como 0,00 mm: ahora son faltantes. Huecos grandes en 2020–2021 y desde septiembre de 2025 |
| Alternativa | SENAMHI (Chulucanas, Partidor) mediante solicitud formal: no tiene API pública |
