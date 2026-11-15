# NASA POWER horario

| Campo | Valor |
| :-- | :-- |
| Endpoint | `https://power.larc.nasa.gov/api/temporal/hourly/point` |
| Autenticación | Ninguna |
| Variables | `t2m_hourly`, `rh2m_hourly`; derivadas diarias `hours_rh90` y `hours_wet_warm` (HR ≥ 90 % y 20–30 °C) |
| Resolución | Celda POWER (~50 km), horaria en hora local |
| Ventana aplicada | máx(2001-01-01, hoy − 10 años), bloques anuales con caché |
| Decisiones que alimenta | Vigilancia de condiciones favorables a antracnosis en mango (V-41, F3) |
| Hallazgo | En marzo de 2024 casi ninguna hora llega a HR ≥ 90 %: la celda regional suaviza la humedad. El indicador necesita humedad de estación o de un sensor en el huerto antes de usarse |
| Limitación | Umbrales POR VALIDAR; se presenta como «condiciones favorables», nunca como probabilidad de infección |
