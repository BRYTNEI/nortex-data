# GAEZ

| Campo | Valor |
| :-- | :-- |
| Endpoint | `gaez-services.fao.org/server/rest/services/res05/ImageServer` (`query` + `identify`) |
| Autenticación | Ninguna |
| Producto / versión | GAEZ v4 (v5 por COG configurable) |
| Resolución | 5 arcmin (~9 km) en v4; 30 arcsec en capas clave de v5 |
| Límites de uso | Una petición `identify` por capa; sin descarga de rásteres |
| Ventana aplicada | No aplica: capas por periodo climático (1961–2100) |
| Rango real obtenido | 125 capas de arroz inundado en 6 periodos |
| Caché | Consulta completa (`get_dataset`) |
| Limitación | Señal de aptitud, nunca filtro (EX-08) |

Producto y variables de origen: v4 res05 ImageServer y capas COG de v4/v5.

La API pública filtra el catálogo de aptitud por cultivo, riego e insumos y pide un píxel de cada capa. La configuración inicial usa Wetland rice con riego por gravedad e insumos altos. Para v5, define version y layers en sources.yaml incluyendo URL HTTPS de COG, cultivo, periodo, escenario, nivel de insumos y unidad. v5 publica capas clave a 30 segundos de arco. Los resultados climáticos no tienen fechas de observación.

[Referencia oficial](https://www.fao.org/statistics/highlights-archive/highlights-detail/what-s-new-in-gaez-v5/en)

En San Lorenzo se consultaron 125 capas para arroz inundado en los periodos 1961–1990, 1971–2000, 1981–2010, 2011–2040, 2041–2070 y 2071–2100. La prueba online también verificó un píxel de la capa 288.
