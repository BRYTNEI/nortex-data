# FAOSTAT

| Campo | Valor |
| :-- | :-- |
| Endpoint | `faostatservices.fao.org/api/v1/en` (`dimensions`, `codes`, `data`) |
| Autenticación | `FAOSTAT_TOKEN` o `FAOSTAT_USERNAME` + `FAOSTAT_PASSWORD` |
| Producto / versión | Dominios QCL y PP |
| Resolución | Nacional (Perú), anual |
| Límites de uso | Códigos descubiertos por API; reintento único ante 401/403 |
| Ventana aplicada | Últimos 10 años publicados |
| Rango real obtenido | 2015–2024 por el portal público; producción QCL de 2024 por la API autenticada |
| Caché | Consulta completa (`get_dataset`) |
| Limitación | Precios nacionales, no de San Lorenzo; usar SIEA para Piura |

Producto y variables de origen: QCL y PP; área cosechada, producción, rendimiento y precio.

La API oficial requiere un token Bearer. `FAOSTAT_TOKEN` vence. Para GitHub Actions, guarda `FAOSTAT_USERNAME` y `FAOSTAT_PASSWORD` como secretos del repositorio. Con ese par, el cliente obtiene un token mediante `POST /auth/login` al conectar, si no hay un token configurado. Si la API rechaza el token, el cliente vuelve a iniciar sesión una vez.

El cliente consulta las dimensiones y los códigos antes de filtrar por área, elemento, cultivo y año. Se verificó que la API autenticada devuelve la producción nacional de Perú para los tres cultivos configurados en 2024.

[Referencia oficial](https://www.fao.org/faostat/en/docs/redoc-static.html)

Se verificó la exportación filtrada del portal público para Perú. Los dominios QCL (área, producción y rendimiento) y PP (valor anual en moneda local por tonelada) aportaron 120 valores válidos de 2015 a 2024. Los tres ítems de FAOSTAT fueron Rice, Mangoes, guavas and mangosteens y Lemons and limes. Los dos grupos de frutas conservan el nombre del agregado publicado.

Los resultados procesados se guardaron en data/processed/faostat-peru-qcl-pp.csv y data/processed/faostat-peru-qcl-pp.parquet. El identificador peru_nacional y las coordenadas vacías preservan el alcance nacional.

**Etiquetas de FAOSTAT.** Los elementos, países y cultivos se buscan primero por coincidencia exacta y, si no existe, por la etiqueta más corta que contenga el texto (p. ej. «Production» encuentra «Production Quantity»). Si no hay ninguna, el error lista las etiquetas que devolvió la API para corregir `config/variables.yaml` o `config/sources.yaml`.
