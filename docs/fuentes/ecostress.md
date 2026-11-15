# ECOSTRESS

Producto y variables de origen: LSTE, JET y ESI C2; LST, ETdaily, ESI, cloud.

El catálogo de AppEEARS sitúa LSTE desde el 9 de julio de 2018 y JET/ESI desde el día 10. El adaptador lee CSV de punto y descarta nube y relleno. ETdaily se convierte de flujo medio diurno a lámina con las horas de luz. ESI alternativo divide la ET por ET0 de la misma fecha y la anomalía usa la media y desviación poblacional del intervalo. Rango de salida pendiente de consulta autenticada.

[Referencia oficial](https://appeears.earthdatacloud.nasa.gov/api/)

Los archivos individuales de resultados puntuales de AppEEARS también se pueden normalizar con import_point_csv(aoi, paths). Se aplica la misma máscara de nubes, conversión de ET y cálculo de ESI que en la ruta API.
