# NASA POWER

| Campo | Valor |
| :-- | :-- |
| Endpoint | `GET https://power.larc.nasa.gov/api/temporal/daily/point` |
| Autenticación | Ninguna |
| Producto / versión | POWER Daily AG, API v2.10.3 (MERRA-2 y CERES) |
| Resolución | 0,5° × 0,625° (radiación ~1°) |
| Límites de uso | Máximo 20 parámetros por petición; un bloque por año |
| Ventana aplicada | máx(1981-01-01, hoy − 10 años) → último dato publicado |
| Rango real obtenido | 2016-11-15 → 2026-11-12 (radiación y ET0 hasta 2026-11-10) |
| Caché | Cada año cerrado en `cache/power-bloque-*.parquet` |
| Alternativa / validación | Estación del aeropuerto de Piura (NOAA GSOD, API abierta) |

Producto y variables de origen: Daily AG y presión corregida PSC.

Verificado en el punto piloto del 1 al 31 de enero de 2025. En una consulta reciente hubo meteorología hasta el 12 de noviembre de 2026, y radiación y ET0 hasta el 10. La API recibe bloques anuales y hasta 20 parámetros diarios. ET0 usa FAO-56 y presión PSC cuando se envía altitud.

[Referencia oficial](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)

La consulta con ventana móvil completa devolvió 36.496 observaciones desde el 15 de noviembre de 2016. Confirmó fechas finales distintas para meteorología y radiación.

**Unidades y caché.** Si la API devuelve una unidad distinta de la del catálogo (por ejemplo kWh/m²/día en lugar de MJ/m²/día), la consulta se detiene: suele indicar una `community` equivocada. Cada año cerrado se guarda como bloque recortado y solo se vuelve a pedir el tramo reciente.
