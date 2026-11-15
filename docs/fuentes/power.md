# NASA POWER

Producto y variables de origen: Daily AG y presión corregida PSC.

Verificado en el punto piloto del 1 al 31 de enero de 2025. En una consulta reciente hubo meteorología hasta el 12 de noviembre de 2026, y radiación y ET0 hasta el 10. La API recibe bloques anuales y hasta 20 parámetros diarios. ET0 usa FAO-56 y presión PSC cuando se envía altitud.

[Referencia oficial](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)

La consulta con ventana móvil completa devolvió 36.496 observaciones desde el 15 de noviembre de 2016. Confirmó fechas finales distintas para meteorología y radiación.

**Unidades y caché.** Si la API devuelve una unidad distinta de la del catálogo (por ejemplo kWh/m²/día en lugar de MJ/m²/día), la consulta se detiene: suele indicar una `community` equivocada. Cada año cerrado se guarda como bloque recortado y solo se vuelve a pedir el tramo reciente.
