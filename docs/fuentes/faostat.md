# FAOSTAT

Producto y variables de origen: QCL y PP; área cosechada, producción, rendimiento y precio.

La API oficial de producción requiere Bearer. Consulta dimensiones y códigos antes de filtrar datos por área, elemento, cultivo y año. El cliente acepta un token externo o un par de usuario y contraseña. Con el par, obtiene AccessToken en POST /auth/login y reactiva la sesión una vez frente a un rechazo del token. El contrato consultado no expone una operación independiente de renovación. La API autenticada no se verificó en este equipo.

[Referencia oficial](https://www.fao.org/faostat/en/docs/redoc-static.html)

Se verificó la exportación filtrada del portal público para Perú. Los dominios QCL (área, producción y rendimiento) y PP (valor anual en moneda local por tonelada) aportaron 120 valores válidos de 2015 a 2024. Los tres ítems de FAOSTAT fueron Rice, Mangoes, guavas and mangosteens y Lemons and limes. Los dos grupos de frutas conservan el nombre del agregado publicado.

Los resultados procesados se guardaron en data/processed/faostat-peru-qcl-pp.csv y data/processed/faostat-peru-qcl-pp.parquet. El identificador peru_nacional y las coordenadas vacías preservan el alcance nacional.
