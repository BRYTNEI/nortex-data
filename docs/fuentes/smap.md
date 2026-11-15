# SMAP

| Campo | Valor |
| :-- | :-- |
| Endpoint | AppEEARS (`appeears.earthdatacloud.nasa.gov/api`); sin credenciales, Zarr público de NASA POWER |
| Autenticación | `EARTHDATA_USERNAME` + `EARTHDATA_PASSWORD` o `APPEEARS_TOKEN`; ninguna para el Zarr |
| Producto / versión | SPL4SMGP.008 |
| Resolución | 9 km (malla EASE 2.0; el Zarr usa la malla nativa 1624 × 3856) |
| Límites de uso | Tareas asíncronas (espera ≤ 30 min); CSV ≤ 5 MB; bloques Zarr ≤ 16 MB |
| Ventana aplicada | máx(2015-03-31, hoy − 10 años) |
| Rango real obtenido | 2016-11-15 → 2026-09-13 por Zarr; AppEEARS pendiente de credenciales |
| Caché | Cada año cerrado (ambas rutas) |
| Limitación | No representa riego; el Zarr no trae bandera de calidad |

Producto y variables de origen: SPL4SMGP.008; Geophysical_Data_sm_surface y Geophysical_Data_sm_rootzone.

El catálogo AppEEARS confirma 31 de marzo de 2015 como inicio y capas a 9 km. Cada bloque anual usa la API de punto. La salida diaria promedia las muestras de tres horas y cuenta muestras válidas. El catálogo consultado no expone una bandera QC dedicada. El polígono usa su punto representativo; Harmony admite recortes de área. La prueba de AppEEARS autenticada sigue pendiente.

[Referencia oficial](https://nsidc.org/data/spl4smgp/versions/8)

Sin credenciales se leen los bloques temporales del [Zarr público de NASA POWER](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/). El archivo diario UTC sirve SFMC y RZMC a ~0,09°. En San Lorenzo se verificó del 15/11/2016 al 13/09/2026. Se registra la ausencia de QC por muestra en el archivo.
