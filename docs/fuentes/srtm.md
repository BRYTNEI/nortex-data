# SRTM 30 m (relieve)

| Campo | Valor |
| :-- | :-- |
| Endpoint | `https://api.opentopodata.org/v1/srtm30m` (cotas de los puntos pedidos) |
| Autenticación | Ninguna; 100 ubicaciones por petición y 1 petición por segundo |
| Variables | `elevation` (m), `slope` (%, Horn 3 × 3), `relief` (m) |
| Resolución | 30 m, estático |
| Rango real obtenido | Punto piloto: 196 m, pendiente 0,6 %. Polígono de ejemplo: 197 m, desnivel 3 m (36 puntos) |
| Decisiones que alimenta | Altitud del sitio para ET0 (§9.1); drenaje y encharcamiento en años El Niño (RT-05, §10.3.1) |
| Hallazgo | **La v0.7 indica 68 m de altitud para el punto de referencia y SRTM da 196 m.** Revisar las coordenadas UTM o la altitud del documento |
