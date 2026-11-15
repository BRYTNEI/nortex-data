# Catálogo de variables

Generado con `python scripts/build_docs.py`.

| ID | Fuente | Producto | Versión | API | Unidad | Espacial | Temporal | Inicio | Inicio aplicado | Método | Fórmula |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tmax | power | POWER Daily AG | v2 | T2M_MAX | C | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| tmin | power | POWER Daily AG | v2 | T2M_MIN | C | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| tmean | power | POWER Daily AG | v2 | T2M | C | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| solar | power | POWER Daily AG | v2 | ALLSKY_SFC_SW_DWN | MJ/m^2/day | 1° solar; 0.5° × 0.625° meteo | diaria | 1984-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| wind2m | power | POWER Daily AG | v2 | WS2M | m/s | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| rh2m | power | POWER Daily AG | v2 | RH2M | % | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| dewpoint | power | POWER Daily AG | v2 | T2MDEW | C | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| pressure | power | POWER Daily AG | v2 | PS/PSC | kPa | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| rain_power | power | POWER Daily AG | v2 | PRECTOTCORR | mm/day | 0.5° × 0.625° | diaria | 1981-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | — |
| et0 | power | POWER Daily AG | v2 | — | mm/day | 1° solar; 0.5° × 0.625° meteo | diaria | 1984-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/daily/point | FAO-56 Penman–Monteith; G=0 |
