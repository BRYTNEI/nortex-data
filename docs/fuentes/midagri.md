# MIDAGRI y SIEA

El [catálogo de campaña agrícola de Piura](https://www.datosabiertos.gob.pe/dataset/campa%C3%B1a-agr%C3%ADcola-de-los-principales-cultivos-de-la-regi%C3%B3n-piura-gobierno-regional-piura-1) publica siembra, cosecha, producción y precio en chacra. La consulta CKAN `package_search` del portal devolvió HTTP 418 en la verificación. El módulo `midagri.py` conserva la búsqueda de metadatos para entornos donde el endpoint responde.

Se extrajeron siete indicadores regionales de arroz de la campaña chica 2024 del anexo 6, páginas 102–103, del [informe oficial ESCO de Piura](https://cdn.www.gob.pe/uploads/document/file/9922537/8096722-publicacion-de-resultados-esco-cultivo-de-arroz-de-piura.pdf?v=1778087772). El CSV procesado local se guardó en `data/processed/midagri-esco-arroz-piura-2024.csv`. Conserva el ámbito, la campaña, la unidad y la página de cada cifra.

El costo directo promedio fue S/ 8.257/ha y el indirecto promedio S/ 780/ha. El informe advierte que los desgloses y agregados se estiman como promedios individuales, por lo que sus componentes no se deben sumar para reconstruir los totales de la encuesta. Las cifras representan la región Piura. Falta una serie de costos a escala de parcela y referencias verificadas para mango y limón en San Lorenzo.
