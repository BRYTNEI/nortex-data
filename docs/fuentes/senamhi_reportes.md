# Reportes hidrológicos de SENAMHI (volumen de reservorios)

| Campo | Valor |
| :-- | :-- |
| Origen | PDF «Información hidrológica diaria» de SENAMHI (`https://www.senamhi.gob.pe/load/file/02603SENA-<n>.pdf`) y PDF guardados en `data/local/reportes_senamhi/` |
| Autenticación | Ninguna |
| Variables | `reservoir_volume_report` (hm³), `reservoir_pct_report` (%), `reservoir_capacity_report` (hm³) para San Lorenzo y Poechos |
| Procedencia del dato | Proyecto Especial Chira Piura y Junta de Usuarios San Lorenzo, publicado por SENAMHI |
| Rango real obtenido | Tres reportes de mayo de 2022 configurados de ejemplo: San Lorenzo 186,04–195,6 hm³ de 195,6 hm³ útiles |
| Decisiones que alimenta | Situación del reservorio (D-17) y dotación análoga cuando no hay PCR (EX-15) |
| Limitación | No hay API ni índice de reportes: hay que añadir las URL o guardar los PDF. La capacidad útil (195,6 hm³) es menor que la de diseño por sedimentación |
| Uso | Agregar URL en `config/sources.yaml` → `senamhi_reportes.reportes`, o copiar PDF a `data/local/reportes_senamhi/` |
