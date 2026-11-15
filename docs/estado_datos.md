# Estado de las fuentes para San Lorenzo

| Fuente | Datos verificados | Trabajo pendiente |
| --- | --- | --- |
| NASA POWER | Meteorología, radiación y ET0 con ventana móvil desde el 15/11/2016 | Actualizar conforme publique nuevos días |
| SMAP | Humedad superficial y radicular por Zarr, hasta el 13/09/2026 | Verificar extracción autenticada de AppEEARS si se necesitan muestras subdiarias |
| GPM / IMERG | Lluvia y extremos por Zarr, hasta el 14/09/2026 | Verificar la vía autenticada cuando se requiera distinguir Final y Late |
| Sentinel-2 | NDRE del polígono en todo 2024 por COG: 73 fechas con escena, 48 con NDRE válido | Probar la Statistical API de CDSE con credenciales y extraer la ventana de 10 años (≈ 1 h la primera vez; luego caché) |
| GAEZ | 125 capas v4 para arroz inundado | Configurar y verificar las capas COG deseadas de v5 |
| FAOSTAT | 120 observaciones de Perú de 2015 a 2024, dominios QCL y PP | Verificar la ruta de API autenticada para automatizar nuevas exportaciones |
| MIDAGRI | Siete indicadores regionales de arroz de la encuesta ESCO, campaña chica 2024 | Verificar costos de mango y limón en San Lorenzo |
| ECOSTRESS | Capas y solicitud histórica confirmadas en AppEEARS | Descargar y validar las observaciones cuando termine la solicitud |
| ENSO (ICEN, ONI) | 1950-01 a 2026-09 | Clasificar años El Niño / La Niña Costera en el motor |
| SoilGrids | Propiedades del suelo del punto piloto (píxel válido a 0,7–1 km) | Sustituir por análisis de laboratorio |
| SRTM | Altitud 196 m, pendiente 0,6 % | Confirmar coordenadas y altitud del punto (la v0.7 dice 68 m) |
| Estación NOAA GSOD | Piura, últimos 10 años con huecos | Solicitar SENAMHI (Chulucanas, Partidor) |
| POWER horario | Marzo 2024 | Humedad local para el indicador de antracnosis |
| Datos locales | Plantillas listas | Reservorio y Quiroz (ANA), PCR y turnos (Junta), economía (SIEA), suelo y agua (laboratorio) |

## ECOSTRESS en proceso

El 15 de noviembre de 2026, AppEEARS registró la solicitud puntual **NORTEX ECOSTRESS 2018-2026 San Lorenzo** del 10 de julio de 2018 al 14 de noviembre de 2026. Contiene LST, ET diaria y ESI a 70 m, con la máscara de nubes de cada producto. En la última revisión del portal figuraba como **Pending**. La página de descarga aún no ofrecía archivos. [Solicitud histórica en AppEEARS](https://appeears.earthdatacloud.nasa.gov/view/1d80e1f7-7a3e-40f3-8d4e-46385eac6c65)

Cuando el estado sea **Done**, entra a AppEEARS con la cuenta que creó la solicitud y descarga los CSV individuales cuyo nombre termina en `-results.csv`. Guárdalos en `data/appeears/ecostress/` y ejecuta desde la raíz del proyecto:

```python
from pathlib import Path

from nortex_data.sources.ecostress import import_point_csv
from nortex_data.utils.core import load_aois

paths = sorted(Path("data/appeears/ecostress").glob("*-results.csv"))
datos = import_point_csv(load_aois()["parcela_01"], paths)
observadas = datos.loc[datos["value"].notna(), "variable"]
faltantes = {"lst", "et_real", "esi"} - set(observadas)
if faltantes:
    raise ValueError(f"Faltan observaciones válidas: {sorted(faltantes)}")
destino = Path("data/processed/ecostress-san-lorenzo-historico.parquet")
destino.parent.mkdir(parents=True, exist_ok=True)
datos.to_parquet(destino, index=False)
```

El repositorio conserva el código, los metadatos y las instrucciones. Los datos y credenciales se guardan en rutas locales ignoradas por Git.
