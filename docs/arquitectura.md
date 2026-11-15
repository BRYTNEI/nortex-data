# Arquitectura

```mermaid
flowchart LR
    AOI["AOI validado"] --> Source["Fuente según catálogo"]
    Source --> API["API con recorte o lectura parcial"]
    API --> Frame["DataFrame con esquema común"]
    Frame --> Cache["Caché Parquet opcional"]
    Frame --> Consumer["CLI, notebook y backend"]
```

- `config/` contiene AOIs, fuentes y catálogo canónico.
- `nortex_data/sources/` contiene los adaptadores.
- `nortex_data/derive/` contiene cálculos reproducibles sobre series recortadas.
- `nortex_data/utils/` contiene validación, HTTP y el cliente AppEEARS.
- `tests/` contiene pruebas offline y consultas online acotadas.
- `scripts/build_docs.py` genera la tabla y sincroniza los archivos de configuración incluidos al instalar.
