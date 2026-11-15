# IMERG

| Campo | Valor |
| :-- | :-- |
| Endpoint | CMR (`cmr.earthdata.nasa.gov`) + OPeNDAP de GES DISC; sin token, Zarr público de NASA POWER |
| Autenticación | `EARTHDATA_TOKEN` (Bearer) para OPeNDAP; ninguna para el Zarr |
| Producto / versión | GPM_3IMERGDF y GPM_3IMERGDL V07 |
| Resolución | 0,1° (también en el Zarr público) |
| Límites de uso | Una petición OPeNDAP por día (~365 por año); respuesta ≤ 16 KB por píxel |
| Ventana aplicada | máx(1998-06-01, hoy − 10 años) |
| Rango real obtenido | 2016-11-15 → 2026-09-14 por Zarr; ruta OPeNDAP pendiente de token |
| Caché | Años cerrados y 100 % Final |
| Alternativa | Giovanni (promedios de área en CSV) |

Producto y variables de origen: GPM_3IMERGDF y GPM_3IMERGDL v07; precipitation.

CMR devuelve los enlaces OPeNDAP. Se solicita un píxel de 0.1° por día, se usa Late después de Final y se conservan banderas de procedencia. Se pueden calcular extremos sobre cualquier intervalo y acumulados de meses completos. Giovanni es una alternativa para promedios espaciales. La prueba OPeNDAP autenticada sigue pendiente.

[Referencia oficial](https://cmr.earthdata.nasa.gov/search/site/collections/directory/GES_DISC/gov.nasa.eosdis)

Sin token se lee la precipitación diaria original de IMERG en el [Zarr público de NASA POWER](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/). El archivo no publica el run por día; se conserva run_unspecified en la salida. Enero de 2025 devolvió 31 días y 24,18 mm acumulados. Se verificó el archivo del 15/11/2016 al 14/09/2026 para el punto piloto.

**Caché y extremos.** Con token de Earthdata cada año cerrado y 100 % Final se guarda como bloque recortado; si contiene días Late se vuelve a pedir. Los umbrales p95 y p99 de los extremos se calculan solo con días húmedos (≥ 1 mm), como R95p de ETCCDI.

**Si Earthdata rechaza el token (401/403).** La consulta OPeNDAP no se detiene: se usa la copia pública de NASA POWER y cada fila queda marcada con `auth_error_fallback` en `qc_flag`. Causas habituales del 403: token vencido (dura 60 días), token copiado con «Bearer» o con espacios (el módulo ya los limpia) o la aplicación «NASA GESDISC DATA ARCHIVE» sin autorizar en el perfil de Earthdata (*Applications → Authorized Apps*). La prueba online falla en ese caso para que el problema quede visible.
