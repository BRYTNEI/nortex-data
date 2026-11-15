# FAOSTAT

Producto y variables de origen: QCL y PP; área cosechada, producción, rendimiento y precio.

La API oficial de producción requiere Bearer. Consulta dimensiones y códigos antes de filtrar datos por área, elemento, cultivo y año. El cliente acepta un token externo o un par de usuario y contraseña. Con el par, obtiene AccessToken en POST /auth/login y reactiva la sesión una vez frente a un rechazo del token. El contrato consultado no expone una operación independiente de renovación. Rango pendiente de consulta autenticada.

[Referencia oficial](https://www.fao.org/faostat/en/docs/redoc-static.html)
