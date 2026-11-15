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
| sm_surface | smap | SPL4SMGP | 008 | Geophysical_Data_sm_surface | m³/m³ | 9 km | diaria (media de 3 h) | 2015-03-31 | max(first, hoy - 10 años) | NASA POWER Zarr diario o AppEEARS; punto representativo | — |
| sm_rootzone | smap | SPL4SMGP | 008 | Geophysical_Data_sm_rootzone | m³/m³ | 9 km | diaria (media de 3 h) | 2015-03-31 | max(first, hoy - 10 años) | NASA POWER Zarr diario o AppEEARS; punto representativo | — |
| precipitation | imerg | GPM_3IMERGDF | 07 | precipitation | mm/day | 0.1° | diaria | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | — |
| rx1day | imerg | GPM_3IMERGDF | 07 | — | mm | 0.1° | intervalo | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | máximo diario |
| rx5day | imerg | GPM_3IMERGDF | 07 | — | mm | 0.1° | intervalo | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | máximo de sumas móviles de cinco días completos |
| days_gt_p95 | imerg | GPM_3IMERGDF | 07 | — | días | 0.1° | intervalo | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | conteo > cuantil 0.95 |
| days_gt_p99 | imerg | GPM_3IMERGDF | 07 | — | días | 0.1° | intervalo | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | conteo > cuantil 0.99 |
| max_dry_days | imerg | GPM_3IMERGDF | 07 | — | días | 0.1° | intervalo | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | racha máxima con lluvia < 1 mm |
| monthly_precip | imerg | GPM_3IMERGDF | 07 | — | mm | 0.1° | mensual | 1998-06-01 | max(first, hoy - 10 años) | NASA POWER Zarr diario (run sin especificar) u OPeNDAP GES DISC mediante CMR | suma de días de un mes completo |
| lst | ecostress | ECO_L2T_LSTE | 002 | LST | K | 70 m | irregular | 2018-07-09 | max(first, hoy - 10 años) | https://appeears.earthdatacloud.nasa.gov/api | — |
| et_real | ecostress | ECO_L3T_JET | 002 | ETdaily | mm/day | 70 m | irregular | 2018-07-10 | max(first, hoy - 10 años) | https://appeears.earthdatacloud.nasa.gov/api | ETdaily × segundos de luz / 2.45e6 J/kg |
| esi | ecostress | ECO_L4T_ESI | 002 | ESI | 1 | 70 m | irregular | 2018-07-10 | max(first, hoy - 10 años) | https://appeears.earthdatacloud.nasa.gov/api | Si no hay ESI válido: ET real / ET0 |
| esi_anomaly | ecostress | ECO_L4T_ESI | 002 | — | 1 | 70 m | irregular | 2018-07-10 | max(first, hoy - 10 años) | https://appeears.earthdatacloud.nasa.gov/api | (ESI − media) / desviación estándar poblacional |
| ndre | s2 | sentinel-2-l2a | L2A | mean | 1 | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| ndre_median | s2 | sentinel-2-l2a | L2A | 50 | 1 | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| ndre_p10 | s2 | sentinel-2-l2a | L2A | 10 | 1 | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| ndre_p90 | s2 | sentinel-2-l2a | L2A | 90 | 1 | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| ndre_std | s2 | sentinel-2-l2a | L2A | stDev | 1 | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| ndre_count | s2 | sentinel-2-l2a | L2A | validCount | píxeles | 20 m | diaria | 2015-06-23 | max(first, hoy - 10 años) | Ventana COG Earth Search o Statistical API CDSE | (B8A − B05) / (B8A + B05), agregado sobre píxeles válidos |
| suitability | gaez | GAEZ | 4 | identify | según capa | 5′ v4; 30″ v5 según capa | periodo climático | 1981-01-01 | No aplica | https://gaez-services.fao.org/server/rest/services | — |
| area_harvested | faostat | QCL | v1 | Area harvested | unidad de la API | Perú | anual | 1961-01-01 | Último año publicado menos 9 | https://faostatservices.fao.org/api/v1/en | — |
| production | faostat | QCL | v1 | Production | unidad de la API | Perú | anual | 1961-01-01 | Último año publicado menos 9 | https://faostatservices.fao.org/api/v1/en | — |
| yield | faostat | QCL | v1 | Yield | unidad de la API | Perú | anual | 1961-01-01 | Último año publicado menos 9 | https://faostatservices.fao.org/api/v1/en | — |
| producer_price | faostat | PP | v1 | Producer Price (LCU/tonne) | unidad de la API | Perú | anual | 1961-01-01 | Último año publicado menos 9 | https://faostatservices.fao.org/api/v1/en | — |
