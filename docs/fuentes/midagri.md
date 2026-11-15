# MIDAGRI y SIEA

El [catálogo de campaña agrícola de Piura](https://www.datosabiertos.gob.pe/dataset/campa%C3%B1a-agr%C3%ADcola-de-los-principales-cultivos-de-la-regi%C3%B3n-piura-gobierno-regional-piura-1) publica siembra, cosecha, producción y precio en chacra. La consulta CKAN `package_search` del portal devolvió HTTP 418 en la verificación. El módulo `midagri.py` conserva la búsqueda de metadatos para entornos donde el endpoint responde.

MIDAGRI publicó resultados de la [Encuesta de Costos de Producción (ESCO) para arroz de Piura](https://www.gob.pe/institucion/uegps/informes-publicaciones/8096722-encuestas-de-costos-de-produccion-esco). La ficha pública identifica un informe PDF. El acceso a la ficha devolvió HTTP 418 en la verificación directa. El catálogo de ESCO consultado también enumera resultados de otros cultivos y regiones. Falta verificar los cuadros del PDF y localizar datos de costo para mango y limón en San Lorenzo.

Para el modelo NORTEX, conserva la campaña, el cultivo, el ámbito geográfico y la unidad de cada cifra. Un resultado regional de la encuesta debe quedar identificado como tal. FAOSTAT aporta estadísticas nacionales de producción y precios.
