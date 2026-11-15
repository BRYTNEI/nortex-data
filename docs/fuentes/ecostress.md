# ECOSTRESS

Producto y variables de origen: LSTE, JET y ESI C2; LST, ETdaily, ESI, cloud.

El catálogo de AppEEARS sitúa LSTE desde el 9 de julio de 2018 y JET/ESI desde el día 10. El adaptador lee CSV de punto y descarta nube y relleno. ETdaily se convierte de flujo medio diurno a lámina con las horas de luz. ESI alternativo divide la ET por ET0 de la misma fecha y la anomalía usa la media y desviación poblacional del intervalo. Rango de salida pendiente de consulta autenticada.

[Referencia oficial](https://appeears.earthdatacloud.nasa.gov/api/)

Los archivos individuales de resultados puntuales de AppEEARS también se pueden normalizar con import_point_csv(aoi, paths). Se aplica la misma máscara de nubes, conversión de ET y cálculo de ESI que en la ruta API.

**Unidad de ETdaily.** El adaptador lee la unidad declarada por AppEEARS para la capa: si es W/m² (flujo medio diurno) convierte a mm/día con las horas de luz; si ya es mm/día la usa tal cual; cualquier otra unidad detiene la consulta. Los CSV importados con `import_point_csv` no traen metadatos: se asume W/m² y se marca `qc_flag = "clear;units_assumed_w_m2"`. El ESI alternativo usa ET0 (cultivo de referencia), no la PET de PT-JPL del ESI oficial, así que sus valores no son directamente comparables.
