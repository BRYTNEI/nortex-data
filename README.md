# NORTEX Data

Paquete de acceso a datos agroclimáticos del piloto de San Lorenzo, Piura.

Instala con `python -m pip install -e ".[dev]"`.
Consulta con `python -m nortex_data fetch --source power --aoi-id parcela_01`.

Fuentes incluidas en esta versión

- [power](docs/fuentes/power.md)
- [imerg](docs/fuentes/imerg.md)
- [smap](docs/fuentes/smap.md)
- [ecostress](docs/fuentes/ecostress.md)

Las credenciales se configuran en .env según las fichas de fuentes.

Consulta el [catálogo](docs/catalogo_variables.md) y la [arquitectura](docs/arquitectura.md).
