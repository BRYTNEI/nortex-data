# IMERG

Producto y variables de origen: GPM_3IMERGDF y GPM_3IMERGDL v07; precipitation.

CMR devuelve los enlaces OPeNDAP. Se solicita un píxel de 0.1° por día, se usa Late después de Final y se conservan banderas de procedencia. Se pueden calcular extremos sobre cualquier intervalo y acumulados de meses completos. Giovanni es una alternativa para promedios espaciales. La prueba OPeNDAP autenticada sigue pendiente.

[Referencia oficial](https://cmr.earthdata.nasa.gov/search/site/collections/directory/GES_DISC/gov.nasa.eosdis)

Sin token se lee la precipitación diaria original de IMERG en el [Zarr público de NASA POWER](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/). El archivo no publica el run por día; se conserva run_unspecified en la salida. Enero de 2025 devolvió 31 días y 24,18 mm acumulados. Se verificó el archivo del 15/11/2016 al 14/09/2026 para el punto piloto.
