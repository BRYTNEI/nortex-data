# Datos locales declarados (sin API)

| Campo | Valor |
| :-- | :-- |
| Origen | CSV en `NORTEX_LOCAL_DIR` (por defecto `data/local`, ignorada por Git) con el formato de `plantillas/` |
| Plantillas | `reservorio`, `caudal_quiroz`, `pcr`, `turnos`, `enfen`, `economia`, `suelo_laboratorio`, `riego_parcela`, `historial` |
| Variables | Reservorio (hm³), caudal Quiroz, área autorizada y dotación del PCR, intervalo de turnos, estado y probabilidad ENFEN, rendimiento/precio/costo, θ_FC/θ_WP/pH/ECe/MO de laboratorio, ECw, napa, profundidad efectiva, eficiencia de riego, rendimiento histórico |
| Categoría | `observado` (registros de ANA y caudales) o `declarado` (usuario, Junta), en `qc_flag`; la fuente de cada fila va en `product` |
| Uso | Copiar la plantilla a `data/local/`, borrar la fila `EJEMPLO` y completar. Si se pide una variable y falta su archivo, el error indica qué plantilla copiar |
| Decisiones que alimenta | Cobertura hídrica y RT-06/RT-08 (PCR, dotación), autonomía (turnos), percentil del reservorio (D-17), conveniencia (margen bruto), RT-05 (ECw, napa), historial para F2 |
| Pendiente | Conseguir los datos reales: ANA (reservorio, Quiroz), Junta de Usuarios San Lorenzo (PCR, turnos), SIEA/MIDAGRI (economía de Piura), laboratorio (suelo y agua) |
