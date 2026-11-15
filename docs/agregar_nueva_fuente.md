# Añadir una fuente o variable

1. Verifica producto, versión, capas, unidades y alcance en el catálogo oficial.
2. Agrega su configuración a `config/sources.yaml` y registra cada identificador en `config/variables.yaml`.
3. Crea o amplía `nortex_data/sources/<fuente>.py`. Implementa `fetch(aoi, start, end, variables=None)` con `frame` y `row` para respetar el esquema común. Registra la fuente en `SOURCES`.
4. Documenta la consulta espacial y temporal, credenciales y límites. Agrega una prueba de un mes y un punto marcada `online`, cuando aplique.
5. Ejecuta `python scripts/build_docs.py`, actualiza la ficha de la fuente y el CHANGELOG y corre Ruff y pytest offline.
