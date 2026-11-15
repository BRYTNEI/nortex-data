# Registro de cambios

## En desarrollo

## 0.6.2

- Validar la lectura de IMERG Final por OPeNDAP y la consulta autenticada de producción de FAOSTAT.
- Integración online #6 sobre `main`: 11 pruebas aprobadas y ECOSTRESS omitida. La importación histórica de ECOSTRESS sigue pendiente de acceso a AppEEARS.

- IMERG: parser OPeNDAP compatible con Hyrax en la nube y diagnóstico con una muestra de la estructura de la respuesta.
- FAOSTAT: filtros compatibles con la API de datos. GitHub Actions puede iniciar sesión automáticamente con los secretos de usuario y contraseña.

- IMERG: si Earthdata rechaza el token (401/403) se usa la copia pública de NASA POWER y se marca `auth_error_fallback`; el token se limpia de «Bearer», espacios y saltos de línea. La prueba online muestra la causa probable.
- FAOSTAT: búsqueda de etiquetas exacta y luego parcial; si falla, el error lista las etiquetas que devolvió la API (la ejecución online #3 falló con «elemento ausente: Production»).

- Fuentes nuevas para las decisiones de la v0.7: `enso` (ICEN y ONI, todo el registro), `soilgrids` (WCS, 9 propiedades × 5 profundidades), `srtm` (altitud, pendiente y desnivel), `estacion` (NOAA GSOD de Piura con tratamiento del atributo `I` en lluvia), `power_horario` (T y HR horarias, horas húmedas) y `local` (9 plantillas CSV para reservorio, PCR, turnos, ENFEN, economía, suelo de laboratorio, riego e historial). Catálogo: 78 variables, 13 fuentes.
- Hallazgos: la altitud SRTM del punto piloto es 196 m (la v0.7 indica 68 m); con POWER horario casi no hay horas con HR ≥ 90 %.

- Corregir `days_gt_p95` y `days_gt_p99`: el percentil se calcula solo con días húmedos (≥ 1 mm), como R95p de ETCCDI. Antes, en San Lorenzo el umbral quedaba cerca de 0 y contaba todos los días con lluvia.
- Caché por bloque anual cerrado en POWER e IMERG (`utils/blocks.py`). Evita repetir ~365 peticiones OPeNDAP por año en IMERG; los años con días Late no se guardan.
- POWER aborta ante una unidad inesperada en lugar de convertir kWh → MJ en silencio (EX-14 de la v0.7).
- ECOSTRESS lee la unidad declarada de `ETdaily` en AppEEARS: convierte solo si es W/m², acepta mm/día y rechaza otras; los CSV importados sin metadatos quedan marcados `units_assumed_w_m2`.
- Caché por bloque anual también en SMAP (Zarr y AppEEARS), Sentinel-2 (CDSE y ventanas COG) y ECOSTRESS.
- Pruebas offline de IMERG (píxel OPeNDAP, enlaces CMR, ruta pública con extremos), SMAP (ruta pública y agregación de 3 horas), Sentinel-2 (respuesta de la Statistical API y resumen COG), GAEZ (`identify` por capa) y FAOSTAT (descubrimiento de códigos y ventana de 10 años).
- Fichas de fuente con tabla resumen: endpoint, autenticación, producto, resolución, límites, ventana, rango real, caché y alternativas.
- CI con Python 3.11 y 3.12.
- Pruebas offline nuevas: regla de 10 años, bloques anuales, AOIs (tamaño y autointersección), valores de relleno, caché (cerrado, reciente, provisional), POWER con una respuesta real guardada, extremos en clima seco y unidades de ECOSTRESS.

- Documentar las coberturas verificadas y cómo incorporar la solicitud histórica pendiente de ECOSTRESS.

- Validar la exportación de FAOSTAT para Perú e importar CSV puntuales de ECOSTRESS.

- Añadir rutas públicas verificadas de SMAP, IMERG y Sentinel-2.
- Incorporar inicio de sesión y reautenticación en FAOSTAT; distinguir el token de AppEEARS.
- Documentar la Encuesta de Costos de Producción para arroz de Piura.

## 0.5.0

- Incorporar GAEZ, FAOSTAT y demo.
- Verificar la ventana móvil completa de NASA POWER para San Lorenzo.

## 0.4.0

- Incorporar estadísticas ndre.

## 0.3.0

- Incorporar ecostress y esi.

## 0.2.0

- Incorporar imerg y humedad smap.

## 0.1.0

- Incorporar nasa power y et0.
