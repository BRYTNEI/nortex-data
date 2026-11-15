# Guía de uso

La configuración de ejemplo incluye el punto piloto y un polígono de demostración. Para agregar una parcela, incluye un punto `lat/lon` o una geometría GeoJSON con coordenadas longitud, latitud, dentro de `aois`. La altitud se indica con `elevation_m`.

```powershell
python -m nortex_data fetch --variables tmax et0 --aoi config/aois.yaml --aoi-id parcela_01 --start 2025-01-01 --end 2025-01-31
```

Desde un notebook o backend, instala el paquete y llama a `get_dataset("power", "parcela_01")`. Usa `variables=["tmax", "ndre"]` como argumento con nombre para que el catálogo resuelva las fuentes. Usa `aoi_path` para pasar un archivo AOI propio. El notebook `notebooks/demo.ipynb` ejecuta una consulta por fuente.

Las variables continuas de fechas subdiarias se representan con la marca temporal que publica la fuente. Los índices agregados solo cuentan las observaciones válidas. Consulta las fichas de fuentes para conocer su escala espacial y sus banderas.
