# NORTEX Data

Paquete Python de acceso a datos para el piloto de San Lorenzo, Tambogrande (Piura). Devuelve observaciones puntuales, estadísticas de parcela y valores nacionales en un esquema común.

## Instalación

```powershell
python -m pip install -e ".[dev,notebook]"
Copy-Item .env.example .env
python -m nortex_data fetch --source power --aoi config/aois.yaml --aoi-id parcela_01 --out data/processed
```

Tras publicar el repositorio privado, los colaboradores con acceso pueden instalarlo mediante `pip install git+https://github.com/BRYTNEI/nortex-data.git`.

```python
from nortex_data import get_dataset

datos = get_dataset(aoi_id="parcela_01", variables=["tmax", "et0"])
```

La salida contiene `date, aoi_id, lat, lon, source, product, variable, value, unit, qc_flag`. La ventana móvil se calcula al consultar. GAEZ identifica el periodo climático en `product` y usa `NaT` en `date`. FAOSTAT devuelve datos nacionales por cultivo y toma hasta diez años anuales de su catálogo. Los adaptadores puntuales usan un punto interior representativo cuando el AOI es un polígono. Sentinel-2 calcula estadísticas sobre el polígono completo.

| Fuente | Producto | Variables | Resolución | Rango verificado en San Lorenzo | Limitación |
| --- | --- | --- | --- | --- | --- |
| NASA POWER | Daily AG | Temperatura, radiación, viento, humedad, presión, lluvia, ET0 | 0.5° × 0.625° meteorología y ~1° solar | Desde 2016-11-15. Meteorología hasta 2026-11-12 y radiación/ET0 hasta 2026-11-10 | Celdas regionales y últimas fechas distintas por variable |
| SMAP | SPL4SMGP.008 | Humedad superficial y radicular | 9 km | 2016-11-15 a 2026-09-13 por Zarr público | Modelo asimilado, bandas públicas sin bandera de calidad dedicada |
| IMERG | GPM_3IMERGDF / GPM_3IMERGDL v07 | Precipitación y extremos | 0.1° | 2016-11-15 a 2026-09-14 por Zarr público | El Zarr deja el run sin especificar. Earthdata distingue Final/Late |
| ECOSTRESS | LSTE / JET / ESI, C2 | LST, ET, ESI y anomalía | 70 m | Solicitud histórica registrada en AppEEARS, en cola en la última revisión | Paso irregular y máscara de nubes |
| Sentinel-2 | L2A | NDRE y estadísticas de píxeles válidos | ~20 m | Enero de 2025, NDRE válido en tres fechas | Sin CDSE, ventanas COG del polígono vía Earth Search |
| GAEZ | v4 ImageServer y v5 por COG configurado | Aptitud para cultivo y escenario | Según capa. v5 ofrece capas clave de ~1 km | 125 capas consultadas para arroz, en seis periodos entre 1961 y 2100 | Capas por periodo climático |
| FAOSTAT | QCL y PP | Área, producción, rendimiento, precio en chacra | Nacional | 2015–2024, 120 valores del portal público | La API autenticada queda por verificar |

## Credenciales

- POWER y GAEZ son públicos. SMAP, IMERG y Sentinel-2 tienen rutas públicas por bloques Zarr y ventanas COG. Configura las credenciales para usar AppEEARS/OPeNDAP/Statistical API cuando corresponda.
- Genera `EARTHDATA_TOKEN` en [NASA Earthdata Login](https://urs.earthdata.nasa.gov/) para IMERG. Para AppEEARS configura `EARTHDATA_USERNAME` y `EARTHDATA_PASSWORD` de esa cuenta. También se admite un token de sesión de AppEEARS en `APPEEARS_TOKEN` para tareas AppEEARS.
- Crea un cliente OAuth en el panel de Sentinel Hub de CDSE y copia su ID y secreto a `CDSE_CLIENT_ID` y `CDSE_CLIENT_SECRET`. [Autenticación de CDSE](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html)
- Regístrate en el portal de desarrolladores de FAOSTAT y configura `FAOSTAT_TOKEN` o `FAOSTAT_USERNAME` y `FAOSTAT_PASSWORD`. Con usuario y contraseña, el cliente vuelve a iniciar sesión ante un 401/403 y reintenta una vez. [Portal de FAOSTAT](https://www.fao.org/faostat/en/#developer-portal)

Las consultas de varias fuentes conservan los resultados parciales y registran los errores en `datos.attrs["errors"]`. La CLI devuelve código 1 si falla alguna fuente. Define `NORTEX_CACHE=0` para desactivar la caché. Si está activa, POWER e IMERG guardan cada año cerrado (fin anterior a hoy − 10 días) como tabla recortada en `cache/*-bloque-*.parquet`; las consultas de los últimos 10 años solo vuelven a pedir el tramo reciente. Los años IMERG con días Late no se guardan hasta que Final los reemplace. Los archivos provistos por las APIs de punto se leen en memoria.

## Pruebas y documentación

```powershell
python -m ruff check .
python -m pytest -m "not online"
python -m pytest -m online
python scripts/build_docs.py --check
```

- [Guía de uso](docs/guia_uso.md)
- [Estado de las fuentes y entrega pendiente de ECOSTRESS](docs/estado_datos.md)
- [Arquitectura](docs/arquitectura.md)
- [Catálogo de variables](docs/catalogo_variables.md)
- [Añadir una fuente](docs/agregar_nueva_fuente.md)
- [Notebook del piloto](notebooks/demo.ipynb)

El catálogo público de Piura incluye siembras, cosecha, producción y precio en chacra. MIDAGRI publica reportes de insumos y servicios y valor bruto agropecuario. Falta verificar una serie homogénea de costos totales por cultivo y campaña de San Lorenzo. [Campaña agrícola de Piura](https://www.datosabiertos.gob.pe/dataset/campa%C3%B1a-agr%C3%ADcola-de-los-principales-cultivos-de-la-regi%C3%B3n-piura-gobierno-regional-piura-1) [Datos de MIDAGRI](https://www.datosabiertos.gob.pe/group/ministerio-de-desarrollo-agrario-y-riego-midagri)

Más detalles y referencia de costos oficiales en la [ficha MIDAGRI/SIEA](docs/fuentes/midagri.md).
