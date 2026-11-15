# Registro de cambios

## En desarrollo

- Corregir `days_gt_p95` y `days_gt_p99`: el percentil se calcula solo con días húmedos (≥ 1 mm), como R95p de ETCCDI. Antes, en San Lorenzo el umbral quedaba cerca de 0 y contaba todos los días con lluvia.
- Caché por bloque anual cerrado en POWER e IMERG (`utils/blocks.py`). Evita repetir ~365 peticiones OPeNDAP por año en IMERG; los años con días Late no se guardan.
- POWER aborta ante una unidad inesperada en lugar de convertir kWh → MJ en silencio (EX-14 de la v0.7).
- ECOSTRESS lee la unidad declarada de `ETdaily` en AppEEARS: convierte solo si es W/m², acepta mm/día y rechaza otras; los CSV importados sin metadatos quedan marcados `units_assumed_w_m2`.
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
