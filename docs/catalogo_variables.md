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
| icen | enso | ICEN (ENFEN 2024, IGP) | oficial | ICEN.txt | C | Niño 1+2 (costa norte del Perú) | mensual | 1950-01-01 | todo el registro | http://met.igp.gob.pe/datos/ICEN.txt | — |
| oni | enso | ONI (NOAA CPC) | v5 | oni.ascii.txt | C | Niño 3.4 (Pacífico central) | trimestral móvil (mes central) | 1950-01-01 | todo el registro | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt | — |
| soil_clay | soilgrids | SoilGrids 2.0 | 2.0 | clay | % | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_sand | soilgrids | SoilGrids 2.0 | 2.0 | sand | % | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_silt | soilgrids | SoilGrids 2.0 | 2.0 | silt | % | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_soc | soilgrids | SoilGrids 2.0 | 2.0 | soc | g/kg | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_ph | soilgrids | SoilGrids 2.0 | 2.0 | phh2o | pH | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_bdod | soilgrids | SoilGrids 2.0 | 2.0 | bdod | kg/dm³ | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_cec | soilgrids | SoilGrids 2.0 | 2.0 | cec | cmol(c)/kg | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | — |
| soil_theta_fc | soilgrids | SoilGrids 2.0 | 2.0 | wv0033 | m³/m³ | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | contenido volumétrico a −33 kPa (capacidad de campo) |
| soil_theta_wp | soilgrids | SoilGrids 2.0 | 2.0 | wv1500 | m³/m³ | 250 m | estática | 2020-01-01 | no aplica | https://maps.isric.org/mapserv (WCS GetCoverage, ventana mínima) | contenido volumétrico a −1500 kPa (punto de marchitez) |
| elevation | srtm | SRTM GL1 30 m (OpenTopoData) | v3 | srtm30m | m | 30 m | estática | 2000-02-11 | no aplica | https://api.opentopodata.org/v1/srtm30m | — |
| slope | srtm | SRTM GL1 30 m (OpenTopoData) | v3 | srtm30m | % | 30 m (malla 3 × 3) | estática | 2000-02-11 | no aplica | https://api.opentopodata.org/v1/srtm30m | Horn sobre malla 3 × 3 de 30 m |
| relief | srtm | SRTM GL1 30 m (OpenTopoData) | v3 | srtm30m | m | 30 m | estática | 2000-02-11 | no aplica | https://api.opentopodata.org/v1/srtm30m | cota máxima − mínima en el AOI |
| station_tmax | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | MAX | C | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| station_tmin | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | MIN | C | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| station_tmean | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | TEMP | C | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| station_dewpoint | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | DEWP | C | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| station_precip | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | PRCP | mm/day | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| station_wind | estacion | NOAA GSOD 84401 (aeropuerto de Piura) | v1 | WDSP | m/s | estación puntual (~33 km del punto piloto) | diaria | 1973-01-01 | max(first, hoy - 10 años) | https://www.ncei.noaa.gov/access/services/data/v1 (global-summary-of-the-day) | — |
| t2m_hourly | power_horario | POWER Hourly AG | v2 | T2M | C | 0.5° × 0.625° | horaria | 2001-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/hourly/point | — |
| rh2m_hourly | power_horario | POWER Hourly AG | v2 | RH2M | % | 0.5° × 0.625° | horaria | 2001-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/hourly/point | — |
| hours_rh90 | power_horario | POWER Hourly AG | v2 | — | h | 0.5° × 0.625° | diaria | 2001-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/hourly/point | horas con HR ≥ 90 % (POR VALIDAR) |
| hours_wet_warm | power_horario | POWER Hourly AG | v2 | — | h | 0.5° × 0.625° | diaria | 2001-01-01 | max(first, hoy - 10 años) | https://power.larc.nasa.gov/api/temporal/hourly/point | horas con HR ≥ 90 % y 20 ≤ T ≤ 30 °C (POR VALIDAR, antracnosis) |
| reservoir_volume | local | plantillas/reservorio.csv | 1 | reservorio | hm³ | reservorio San Lorenzo | según registro | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| quiroz_flow | local | plantillas/caudal_quiroz.csv | 1 | caudal_quiroz | m³/s | río Quiroz, estación Zamba | según registro | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| pcr_area_authorized | local | plantillas/pcr.csv | 1 | pcr | ha | comisión de regantes | campaña | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| water_allocation | local | plantillas/pcr.csv | 1 | pcr | m³/ha | comisión de regantes | campaña | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| turn_interval | local | plantillas/turnos.csv | 1 | turnos | días | comisión de regantes | campaña | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| enfen_alert_state | local | plantillas/enfen.csv | 1 | enfen | código (0 no activo, 1 vigilancia, 2 alerta) | nacional | por comunicado | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| enfen_prob_nino | local | plantillas/enfen.csv | 1 | enfen | % | nacional | por comunicado | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| yield_reference | local | plantillas/economia.csv | 1 | economia | t/ha | según ámbito declarado | anual | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| price_farmgate | local | plantillas/economia.csv | 1 | economia | S/./kg | según ámbito declarado | anual | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| cost_production | local | plantillas/economia.csv | 1 | economia | S/./ha | según ámbito declarado | anual | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| lab_theta_fc | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | m³/m³ | muestra de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| lab_theta_wp | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | m³/m³ | muestra de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| lab_ph | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | pH | muestra de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| soil_ec | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | dS/m | muestra de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| soil_om | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | % | muestra de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| water_ec | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | dS/m | agua de riego de la parcela | por muestreo | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| water_table_depth | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | m | parcela | por medición | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| soil_effective_depth | local | plantillas/suelo_laboratorio.csv | 1 | suelo_laboratorio | m | parcela | por calicata | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| application_efficiency | local | plantillas/riego_parcela.csv | 1 | riego_parcela | 1 | parcela | declarada | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| history_yield | local | plantillas/historial.csv | 1 | historial | t/ha | parcela | por campaña | 1900-01-01 | todo lo declarado | CSV en data/local según plantillas/ | — |
| reservoir_volume_report | senamhi_reportes | SENAMHI Información hidrológica diaria (PDF) | 2022+ | Volumen almacenado | hm³ | reservorio (San Lorenzo, Poechos) | por reporte | 2016-01-01 | todos los reportes configurados | https://www.senamhi.gob.pe/load/file/02603SENA-<n>.pdf o data/local/reportes_senamhi | — |
| reservoir_pct_report | senamhi_reportes | SENAMHI Información hidrológica diaria (PDF) | 2022+ | Porcentaje de la capacidad | % | reservorio (San Lorenzo, Poechos) | por reporte | 2016-01-01 | todos los reportes configurados | https://www.senamhi.gob.pe/load/file/02603SENA-<n>.pdf o data/local/reportes_senamhi | — |
| reservoir_capacity_report | senamhi_reportes | SENAMHI Información hidrológica diaria (PDF) | 2022+ | Capacidad útil | hm³ | reservorio (San Lorenzo, Poechos) | por reporte | 2016-01-01 | todos los reportes configurados | https://www.senamhi.gob.pe/load/file/02603SENA-<n>.pdf o data/local/reportes_senamhi | — |
