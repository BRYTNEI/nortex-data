# **NORTEX — Documentación de la solución propuesta**

## *Horizonte de una campaña, estimación de condiciones futuras y contrato de variables revisado*

Versión: 0.7  \|  Fecha: 14 de noviembre de 2026
Proyecto: NASA Space Apps Challenge 2026  \|  Reto: Field Shift: Adapting Farms with NASA Data
Zona piloto: sector San Lorenzo, distrito de Tambogrande, Piura, Perú
Tipo de documento: propuesta de arquitectura y contrato de variables. **No es evidencia de que los datos estén integrados.**
Base: auditoría técnica `AUDITORIA_NORTEX_v0.6.md`.

> **Cambios de la v0.7 respecto a la v0.6**
> 1. **Prioridad hídrica invertida:** volumen del reservorio, Plan de Cultivo y Riego (PCR), dotación y turnos pasan a **Esenciales**; SPI baja a contexto y SPEI se difiere (§7.1, §10).
> 2. **ET0 completa:** se documentan Ra, Rso y Rnl, con prueba de aceptación contra FAO-56 (§9.1).
> 3. **Balance hídrico corregido:** se usa la forma FAO-56 en agotamiento (Dr) con **ETc,adj = Ks·Kc·ET0**, no ETc (§9.3).
> 4. **SPI con tratamiento de ceros** (distribución mixta) (§10.1).
> 5. **POWER con `community=AG`** y validación de unidades en la respuesta (§7.2).
> 6. **Enum único de seis categorías de dato** (§6.1, §13).
> 7. **El Niño Costero con años análogos individuales** y serie 1981–2025; índice **ICEN** en lugar de solo "estado ENSO" (§6.3).
> 8. Nuevas derivadas: **cobertura hídrica** (§9.4), **autonomía entre turnos** (§9.5) y **noches frescas para inducción floral del mango** (§9.6).
> 9. Nuevas variables: PCR, intervalo de turnos, ICEN, ECw, napa freática, sistema de riego, variedad de mango (§8.1).
> 10. Corrección de la tolerancia salina del **caupí** (§5.2).
> 11. **ECOSTRESS** reposicionado como la fuente NASA que ve el efecto del riego (§7.1).
> 12. Decisiones explícitas: **sin ML en el MVP** y **sin "score de resiliencia"** (§2).
> 13. Requisitos nuevos y criterios de aceptación con plantilla ISO/IEC/IEEE 29148 (§17).
> 14. Referencias cruzadas corregidas.

---

# **Cómo leer este documento**

| Estado | Significado |
| :---- | :---- |
| ACORDADO | Decisión adoptada como alcance actual. |
| PROPUESTO | Diseño técnico recomendado, sujeto a discusión. |
| POR VALIDAR | Requiere datos, revisión agronómica o confirmación local. |
| DIFERIDO | Reconocido como necesario, pero fuera del MVP. |

## **Resumen en una frase**

NORTEX ayuda a un productor del valle de San Lorenzo a decidir **qué cultivar en la próxima campaña y cuándo sembrarlo**, combinando datos NASA verificados con el historial y las condiciones declaradas de su parcela, mostrando siempre qué es observado, qué es estimado y qué falta.

---

# **1. Propósito y problema**

NORTEX es un sistema de apoyo a decisiones para productores de San Lorenzo. Convierte clima, suelo, agua e historial en evaluaciones comprensibles, **no en predicciones exactas ni órdenes automáticas**.

Dos realidades locales condicionan el diseño:

1. **El valle es agrícola con riego**, dependiente del reservorio San Lorenzo y de la Junta de Usuarios. El agua es una restricción operativa, no un supuesto.
2. **Los cultivos principales no son todos anuales.** Arroz es anual; mango y limón son perennes con vida productiva de décadas.

De ahí la decisión de horizonte: **una campaña**. Es lo que el agricultor realmente decide y lo que los datos disponibles permiten sostener.

---

# **2. Decisiones de alcance**

| Tema | Decisión |
| :---- | :---- |
| **Horizonte** | **ACORDADO: una sola campaña.** Se elimina el cronograma multianual. |
| **Rotación** | ACORDADO: se mantiene como comparación **continuidad vs cambio** para la próxima campaña, a partir del historial. |
| Funciones | ACORDADO: F1 cultivo→ventanas; F2 periodo→cultivos y transición; F3 cultivo establecido→seguimiento. |
| Catálogo | ACORDADO: arroz, mango, limón sutil + **un cultivo anual adicional para demostrar rotación convencional** (§6). |
| Perennes | ACORDADO: se evalúan como opción de la campaña, declarando que comprometen 20 años. |
| Parcela | ACORDADO (v0.6): **dibujo manual en el mapa**. El levantamiento GPS se difiere. |
| Recomendación | ACORDADO: cuatro dimensiones separadas (viabilidad, riesgo, conveniencia, fundamentación). |
| Fuentes | ACORDADO (v0.6): tres niveles de prioridad (§7). |
| Regla de no invención | ACORDADO: sin índices compuestos sin fórmula, pesos y validación. Sin "salud del suelo 0–100" ni "probabilidad de pérdida". |
| Agua | ACORDADO (v0.7): la restricción dominante es **hidrológica y operativa** (reservorio, PCR, turnos), no la lluvia local. |
| Aprendizaje automático | ACORDADO (v0.7): **sin ML en el MVP.** No existe historial etiquetado (rendimientos, pérdidas, fechas de floración por parcela) con qué entrenarlo ni validarlo. Se reconsidera cuando el historial lo permita. |
| "Score de resiliencia" | ACORDADO (v0.7): **no se calcula.** Se sustituye por una **ficha de preparación de la campaña**: ítems verificables (✔ / ✘ / desconocido), sin suma ni ponderación (§15). |
| Nombre del módulo de riesgo | ACORDADO (v0.7): **"Riesgo por escenario"**, no "predicción", para no contradecir §6. |

## **2.1. Referencia geográfica**

Punto de referencia: UTM WGS 84 zona 17M, Este 573 124 m, Norte 9 436 951 m, altitud 68 m s. n. m. Equivalente aproximado: latitud −5.093608°, longitud −80.340280° (EPSG:32717).

Sirve para las primeras consultas. **No sustituye el polígono de la parcela**, que se dibuja manualmente (§12).

---

# **3. Las tres funciones**

| Función | Pregunta | Horizonte | Salida |
| :---- | :---- | :---- | :---- |
| **F1** | Tengo un cultivo: ¿cuándo conviene sembrarlo? | Próxima campaña | Calendario de ventanas con riesgos por etapa |
| **F2** | Tengo un periodo: ¿qué conviene sembrar? | Próxima campaña | Comparación de cultivos y transición desde el historial |
| **F3** | Ya sembré: ¿qué debo vigilar? | Semana a semana | Informe preventivo por etapa |

Las tres comparten el mismo motor. Cambia la pregunta, no la lógica.

## **3.1. F1 — ¿Cuándo conviene sembrar?**

1. El agricultor elige un cultivo del catálogo y confirma las condiciones de la parcela.
2. NORTEX genera ventanas candidatas dentro de la próxima campaña según el ciclo documentado.
3. Para cada ventana proyecta etapas fenológicas (GDD) y las contrasta con los escenarios climáticos.
4. Presenta periodos potencialmente favorables, riesgos por etapa y grado de fundamentación.

**Salida:** calendario de ventanas con explicaciones, restricciones y enlace a la evaluación de qué cultivo podría seguir.

## **3.2. F2 — ¿Qué conviene sembrar?**

1. El agricultor indica mes o ventana tentativa y las condiciones de la parcela.
2. El sistema compara los cultivos candidatos por ciclo y etapas críticas.
3. El motor de rotación usa el historial (p. ej. arroz → ¿frijol, maíz o arroz?) para valorar compatibilidad de transición.
4. Se comparan alternativas en las cuatro dimensiones; el agricultor decide.

**Salida:** comparación razonada de cultivos y transiciones para la próxima campaña, no una secuencia fija a varios años.

## **3.3. F3 — ¿Qué debo vigilar?**

1. El usuario registra cultivo, fecha de siembra o etapa observada y manejo.
2. El sistema reúne observaciones recientes y, si existen, pronósticos verificables.
3. Estima la etapa, permite corregirla y evalúa riesgos por etapa.
4. Presenta informe preventivo: condiciones observadas, riesgos, datos faltantes y precauciones.
5. Al cosechar, el resultado pasa al historial.

---

# **4. Rotación con horizonte de una campaña**

## **4.1. Qué significa ahora**

Con una sola campaña, la rotación **no desaparece**: cambia de pregunta.

> No: "¿qué secuencia de 3 años me conviene?"
> Sí: "dado lo que sembré antes, ¿qué elijo **esta** campaña: repetir, cambiar o descansar?"

Eso es exactamente lo que el agricultor decide en la práctica, y es defendible con los datos disponibles.

## **4.2. Los tres tipos de decisión de la campaña**

| Tipo | Pregunta | Ejemplo |
| :---- | :---- | :---- |
| **Continuidad** | ¿Repito el mismo cultivo? | Arroz → arroz |
| **Cambio** | ¿Paso a otro cultivo anual? | Arroz → frijol caupí |
| **Transición** | ¿Instalo o mantengo un perenne? | Arroz → mango (compromiso de 20 años) |

Los tres se evalúan con el mismo motor, pero **la tercera lleva advertencia explícita** porque no es reversible.

## **4.3. Cómo se evalúa la transición en un horizonte de una campaña**

No se simulan 20 años. Se evalúa **la decisión de este año** y se declaran sus consecuencias:

| Se evalúa ahora | Se declara como consecuencia |
|---|---|
| ¿El suelo sirve? (drenaje, salinidad, profundidad) | Si no, "no viable bajo condiciones actuales" |
| ¿Hay agua disponible? | Sin agua, el perenne no es viable |
| ¿Hay capital para 3–4 años sin ingreso? | Si no, "agronómicamente viable, financieramente no viable" |
| ¿Qué se gana o pierde esta campaña? | Ingreso cero o negativo durante el juvenil |
| ¿Qué compromiso se asume? | 20 años, con punto de no retorno en el año 4 |

**Regla editorial:** NORTEX puede recomendar la transición, pero **nunca sin mostrar el compromiso**.

## **4.4. Reglas de transición — reclasificadas**

La v0.5 presentaba siete reglas como si todas tuvieran el mismo respaldo. No es así. Se separan en tres categorías:

| ID | Regla | Categoría | Estado |
| :---- | :---- | :---- | :---- |
| RT-01 | Un perenne en producción no cambia de cultivo sin decisión explícita de renovación | Restricción conceptual | ACORDADO |
| RT-02 | Instalar perenne implica declarar 3–4 años sin ingreso | Advertencia declarativa | ACORDADO |
| RT-03 | El intercalado requiere agua y luz suficientes | Condición agronómica | POR VALIDAR con ficha |
| RT-04 | ~~Arroz–arroz más de 2 campañas = degradación~~ | **Señal sin respaldo suficiente** | **DEGRADADA a advertencia informativa, no regla automática** |
| RT-05 | Paso de arroz a frutal exige verificar drenaje y salinidad | Lista de verificación | ACORDADO |
| RT-06 | La opción no puede exceder el agua asignada (dotación del PCR); se evalúa con la cobertura hídrica C (§9.4) | Restricción verificable | ACORDADO solo si hay dato |
| RT-08 | Si el PCR no autoriza área del cultivo en la campaña, la opción es "no viable por asignación", independientemente de su aptitud agronómica | Restricción institucional | ACORDADO (v0.7) |
| RT-07 | Toda transición declara qué dato falta para confirmarla | Regla de transparencia | ACORDADO |

> **Nota:** RT-04 se conserva como texto informativo ("dos campañas consecutivas de arroz es un patrón que conviene revisar con un técnico"), pero **no descarta ni penaliza automáticamente**. Requiere respaldo agronómico local antes de convertirse en regla.

---

# **5. Catálogo de cultivos**

## **5.1. Qué cultivo agregar para demostrar rotación convencional**

**Recomendación: frijol caupí (*Vigna unguiculata*), también llamado frijol castilla.**

Es la incorporación de mayor valor por unidad de esfuerzo, por seis razones:

| Razón | Detalle |
|---|---|
| **Es anual** | Entra en la lógica de rotación sin complicaciones |
| **Es leguminosa** | Fija nitrógeno y rompe el ciclo de patógenos del arroz: es **el ejemplo de libro** de rotación |
| **Ciclo corto** | 70–90 días; cabe en la ventana posterior al arroz usando humedad residual |
| **Bajo requerimiento de agua** | No compite con el arroz por el reservorio |
| **Mercado real en Piura** | El frijol castilla es un cultivo comercial establecido en la región |
| **Bajo costo de instalación** | No distorsiona la comparación económica |

Con esto puedes demostrar **tres rotaciones clásicas**:

```
arroz → frijol caupí → arroz     (cereal–leguminosa)
arroz → maíz → arroz             (cereal–cereal, si se agrega maíz)
arroz → descanso → arroz         (descanso / abono verde)
```

**Segunda incorporación opcional: maíz amarillo duro.** Aporta la pata "cereal" de la rotación cereal–leguminosa, tiene mercado regional y ciclo compatible. Si solo pueden agregar uno, agreguen **caupí**; si pueden dos, agreguen **caupí + maíz**.

**Sobre camote:** es anual y fue candidato previo, pero su cosecha remueve mucho suelo y complica la comparación de "efecto de la rotación". Sirve como tercera opción, no como primera.

## **5.2. Tabla del catálogo**

> **Rangos indicativos de literatura. Estado: POR VALIDAR con fichas INIA / MIDAGRI antes de usarlos en el motor.**

| Parámetro | Arroz | Frijol caupí | Maíz amarillo duro | Mango | Limón sutil |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Nombre científico | *Oryza sativa* | *Vigna unguiculata* | *Zea mays* | *Mangifera indica* | ***Citrus × aurantiifolia*** |
| Tipo | Anual | Anual | Anual | Perenne | Perenne |
| Ciclo / vida | 120–150 d | 70–90 d | 110–140 d | 20–30 años | 15–25 años |
| Periodo juvenil | — | — | — | 3–4 años | 3–4 años |
| Kc (rango) | 1,05–1,20 | 0,60–0,90 | 0,80–1,15 | 0,50–0,90 | 0,60–0,90 |
| Profundidad radicular | 0,4–0,6 m | 0,5–0,9 m | 0,8–1,2 m | 1,5–2,0 m | 0,9–1,2 m |
| Demanda anual de agua | 10 000–15 000 m³/ha | 3 000–4 500 m³/ha | 6 000–8 000 m³/ha | 6 000–9 000 m³/ha | 7 000–10 000 m³/ha |
| Tolerancia a salinidad (umbral ECe) | ~3,0 dS/m | **~4,9 dS/m** (FAO-29, POR VERIFICAR) | ~1,7 dS/m | ~1,5–2,0 dS/m | ~1,5–1,7 dS/m |
| Drenaje | Tolera anegamiento | Requiere buen drenaje | Sensible al encharcamiento | Sensible | Muy sensible |
| Fijación de N | No | **Sí (simbiótica)** | No | No | No |
| Papel en la rotación | Cabeza de secuencia | **Rompe ciclo / aporta N** | Alternativa cereal | Compromiso de largo plazo | Compromiso de largo plazo |
| Riesgo principal | Agua del reservorio, salinidad | Mosca blanca, virus, humedad excesiva | Gusano cogollero, sequía en floración | Inducción floral, antracnosis, mosca de la fruta | Salinidad, *Phytophthora*, tristeza |
| Decisión crítica de la campaña | Fecha de siembra y área autorizada en el PCR | Fecha de siembra tras el arroz | Fecha de siembra | **Inducción floral (invierno) y floración** — no hay "fecha de siembra" | Floración y cuajado; manejo del agua |
| Variedad a declarar | — | — | — | **Kent / Haden / Edward / otra** (fenología distinta) | Limón sutil (confirmar) |

### **Nota obligatoria sobre el limón**

**No es *Citrus limon*.** El limón que se cultiva y comercializa en Piura es el **limón sutil** (*Citrus × aurantiifolia*), especie distinta del limón italiano o Eureka (*Citrus × limon*).

| | Limón sutil | Limón italiano / Eureka |
| :---- | :---- | :---- |
| Especie | *Citrus × aurantiifolia* | *Citrus × limon* |
| Fruto | Pequeño, muy ácido, semillas | Grande, ovalado, pocas semillas |
| Uso en Piura | Cultivo comercial principal | Marginal |
| Tolerancias | **No transferibles sin revisión** | **No transferibles sin revisión** |

Los parámetros de la tabla son referencias generales de cítricos. **Antes de asignar Kc, tolerancia a salinidad o umbrales térmicos, el equipo debe confirmar la especie y usar la ficha correspondiente.** Usar valores de *C. limon* para *C. aurantiifolia* es un error que un jurado agronómico detectaría.

---

# **6. Cómo se estiman las condiciones futuras**

Esta sección responde a la observación: *"falta especificar cómo estimarán las condiciones futuras"*.

## **6.1. Seis categorías de dato que nunca se mezclan**

> **Corrección v0.7:** la v0.6 decía "tres categorías", listaba cuatro y §13 usaba cinco. Se fija un **enum único de seis valores**, usado en toda la interfaz, el ETL y los metadatos.

| Categoría (`data_category`) | Definición | Ejemplo | Qué se puede afirmar |
| :---- | :---- | :---- | :---- |
| **observado** | Medido en estación o reportado por un organismo para una fecha pasada | Estación SENAMHI, volumen del reservorio (ANA), ICEN histórico | "Ocurrió / se midió" |
| **modelado** | Estimación de un producto de reanálisis, satélite o asimilación para una fecha pasada | POWER 2015-03-12, IMERG 2024-02-15, SMAP L4 | "El producto estima que ocurrió, a esta resolución" |
| **pronosticado** | Emitido por un servicio, con horizonte, fecha de emisión y probabilidad | Comunicado ENFEN, pronóstico trimestral SENAMHI | "El servicio estima, con esta fecha y este horizonte" |
| **escenario** | Construido por NORTEX a partir del histórico | P10 / P50 / P90, año análogo | "Si se repitieran condiciones como estas" |
| **simulado** | Resultado del modelo físico con un escenario dado | ETc, balance, cobertura hídrica, riesgo por etapa | "El modelo calcula que…" |
| **declarado** | Aportado por el usuario o un técnico, sin verificación de NORTEX | Suelo, historial, dotación, intervalo de turnos | "El usuario informa que…" |

**Regla:** cada número de la interfaz lleva su etiqueta. No existe un número "neutro".

## **6.2. Cómo se construye un escenario (procedimiento)**

1. **Serie base:** 30 años de POWER diario (1991–2020, normal climatológica) para los percentiles, con control de calidad y detección de huecos. Para años análogos y estratificación ENSO se usa **toda la serie disponible (1981–2025)**.
2. **Agregación estacional:** acumulados de precipitación y medias de temperatura por la ventana de la campaña (no por año calendario).
3. **Distribución empírica:** se ordenan los 30 valores y se toman los percentiles **10, 50 y 90**.
4. **Año análogo:** se identifica el año histórico más cercano a cada percentil (más interpretable que un valor abstracto).
5. **Propagación:** con el escenario elegido se recalculan ET0, GDD, ventana de siembra y balance.
6. **Etiquetado:** el escenario se muestra siempre como "escenario", con su percentil y su año análogo.

**Lo que NO se hace:**
- No se presenta el percentil 10 como "va a llover poco".
- No se asigna probabilidad al escenario salvo que provenga de un pronóstico oficial.
- No se extrapola la tendencia histórica como proyección climática.

## **6.3. Condicionamiento por ENSO (con advertencias)**

PROPUESTO: estratificar la muestra histórica según el estado ENSO **costero** del año.

**Índice de clasificación (v0.7):** el **ICEN** (Índice Costero El Niño, región Niño 1+2) publicado por ENFEN, porque describe el calentamiento frente a la costa norte peruana, que es el que afecta a Piura. El **ONI** (Niño 3.4, NOAA) se muestra como contexto del Pacífico central, no como clasificador.

```
Años neutros (muestra grande)     → escenario base con percentiles P10/P50/P90
Años El Niño Costero (muestra chica) → años análogos individuales (p. ej. 1983, 1998, 2017, 2023 — POR VERIFICAR con ICEN)
Años La Niña (muestra chica)         → años análogos individuales
```

> **Corrección v0.7:** con 30 años, la categoría El Niño Costero nunca alcanzaba 10 años y EX-07 desactivaba en la práctica el escenario condicionado. Ahora, si la categoría tiene **menos de 10 años**, no se calculan percentiles: **se muestran los años análogos uno por uno**, con sus valores reales, lo que además es más interpretable para el agricultor.

**Advertencias obligatorias:**

1. La muestra condicionada es pequeña: los años análogos son ilustraciones, no una distribución.
2. **La relación no es determinista.** En Piura, El Niño Costero se asocia con mayor probabilidad de lluvias extremas y La Niña con mayor probabilidad de déficit, pero **SENAMHI documenta también escenarios de sequía en años El Niño**. No es una regla.
3. La clasificación de cada año histórico proviene del **ICEN oficial**, no de una impresión.
4. **El Niño Costero no es solo lluvia.** También implica **invierno cálido** (riesgo de falla de inducción floral del mango, §9.6), problemas de drenaje y mayor presión de plagas y enfermedades.

### **6.3.1. Integración de los comunicados ENFEN**

| Elemento del comunicado | Cómo entra | Categoría |
| :---- | :---- | :---- |
| Estado del sistema de alerta | Etiqueta de la campaña en pantalla | pronosticado |
| Probabilidades de magnitud de El Niño Costero para el próximo verano | Se muestran **en paralelo** con los años análogos; no se fusionan en un solo número | pronosticado |
| ICEN mensual histórico | Clasifica los años de la serie | observado |

```
ENFEN (emitido AAAA-MM-DD, horizonte dic–mar): P(El Niño Costero moderado o mayor) = X %
Escenario base (años neutros):    P10 / P50 / P90
Años análogos El Niño Costero:    1983 · 1998 · 2017 · 2023  (valores individuales)
```

> **Corrección respecto a la v0.5:** la v0.5 afirmaba "en Piura la sequía se asocia a La Niña, no a El Niño". Esa formulación era demasiado categórica. La versión correcta es: **es una tendencia estadística, no una regla, y existe evidencia de sequías en años El Niño.**

## **6.4. Integración de pronóstico oficial**

Solo se integra si la fuente publica: horizonte, fecha de emisión, probabilidad y área de cobertura.

| Requisito | Por qué |
|---|---|
| Fecha de emisión y caducidad | Un pronóstico vencido no es información |
| Horizonte explícito | Un trimestral no resuelve eventos diarios |
| Probabilidad declarada | Sin ella, no se puede presentar como probabilidad |
| Cobertura geográfica | El pronóstico de la región Piura no es el de la parcela |
| Verificación histórica del servicio | Sin skill conocido, no se pondera |

**Regla:** el pronóstico **no reemplaza** al escenario. Se muestran en paralelo: "el servicio estima X (emitido el día Y, horizonte Z); el escenario histórico equivalente es W".

## **6.5. Validación (hindcast)**

Antes de confiar en un escenario, se prueba contra el pasado:

1. Se construyen escenarios con datos hasta el año *t−1*.
2. Se compara con lo observado en el año *t*.
3. Se repite para 10–15 años.
4. Se reporta: frecuencia con que lo observado cayó dentro del rango P10–P90.

Si el rango no contiene lo observado al menos 7 de cada 10 años, el escenario está mal calibrado y se declara.

> **Precisión v0.7:** por construcción, P10–P90 debería contener ~80 % de los años. Con 10–15 años el test discrimina poco, así que la cobertura se reporta **con su intervalo de confianza binomial** (p. ej. "11 de 14 años, IC 95 %: 49–95 %"), no solo como aprobado/reprobado.

## **6.6. Qué se puede y qué no se puede proyectar**

| Variable futura | Método | Etiqueta | ¿Válido en el MVP? |
| :---- | :---- | :---- | :---: |
| Precipitación de la campaña | Percentiles históricos + año análogo | Escenario | ✅ |
| Tmax / Tmin | Percentiles históricos | Escenario | ✅ |
| ET0 | Calculada con T, Rs y viento del escenario | Derivada de escenario | ✅ |
| GDD | Calculada con Tmax/Tmin del escenario | Derivada de escenario | ✅ |
| Humedad del suelo | **No se pronostica**: se simula con el balance, partiendo de la última condición conocida (riego declarado; SMAP solo en secano o años de lluvia) | Simulado | ✅ (condicionado) |
| Noches frescas (inducción floral) | Conteo observado a la fecha + percentiles históricos para el resto del invierno | Modelado + escenario | ✅ |
| Dotación de riego de la campaña | **No se pronostica**: se lee del PCR; si aún no existe, dotación de la campaña análoga en volumen | Declarado / escenario | ✅ |
| Estado ENSO | Pronóstico oficial ENFEN | Pronosticado | ○ si hay fuente |
| Precio del cultivo | **No se pronostica**: referencia actual + análisis de sensibilidad | Referencia | ✅ |
| Rendimiento | **No se pronostica**: referencia regional + banda | Referencia | ✅ |
| Eventos extremos diarios | Solo frecuencia histórica, no fecha | Escenario | ○ |

## **6.7. Reglas de presentación**

1. Todo dato lleva: valor, unidad, fuente, fecha de referencia, resolución y **etiqueta de categoría**.
2. Las seis categorías tienen color, ícono y texto distintos, no solo color (accesibilidad).
3. Si un pronóstico caduca durante la sesión, se marca como vencido.
4. Nunca se escribe "se espera" sin indicar quién lo espera y con qué horizonte.
5. La frase "escenario seco" siempre va acompañada de "percentil 10 de los últimos 30 años".

---

# **7. Datos y fuentes en tres niveles**

## **7.1. Clasificación**

| Nivel | Fuentes | Finalidad | En el MVP |
| :---- | :---- | :---- | :---: |
| **Esenciales para empezar** | NASA POWER · datos declarados de suelo · historial agrícola · catálogo de cultivos | Construir y probar el primer motor de evaluación | ✅ |
| **Esenciales — agua (v0.7)** | Volumen del reservorio San Lorenzo (ANA) · PCR y dotación (Junta de Usuarios) · intervalo de turnos (declarado) · ICEN (ENFEN) | Evaluar la restricción que de verdad decide la campaña | ✅ (entrada manual si no hay API) |
| **Complementarias importantes** | GPM IMERG · SENAMHI (estación más cercana) · SMAP L4 · caudal del río Quiroz · SPI | Mejorar precipitación en años El Niño y contexto de sequía | ✅ parcial |
| **Fase posterior** | ECOSTRESS · Sentinel-2 · SPEI · índices avanzados · FAO GAEZ · modelos económicos detallados | Ampliar seguimiento, comparaciones y fundamentación | ❌ |

> **Cambio v0.7 — prioridad hídrica invertida.** En un valle hiperárido con riego regulado, la lluvia local es marginal en años normales. La sequía que decide la campaña es **hidrológica y operativa** (reservorio, PCR, turnos). Por eso esas variables suben a Esenciales y SPI/SPEI bajan.

| Tipo de sequía | Indicador | ¿Decide la campaña en San Lorenzo? |
| :---- | :---- | :---- |
| Meteorológica | SPI | Casi nunca: la lluvia es marginal en años normales |
| Agroclimática | SPEI | Poco: describe la atmósfera, no el agua aplicada |
| **Hidrológica / operativa** | Reservorio, caudal Quiroz, PCR, turnos | **Sí: restricción dominante** |
| Agronómica | ETa/ETc y cobertura hídrica del balance con riego declarado | Sí, a nivel de parcela |

> **ECOSTRESS (fase posterior, pero con papel definido):** es la **única fuente NASA disponible que mide el efecto del riego** (ET real y temperatura de dosel a ~70 m). SMAP no lo ve. Su uso previsto es F3 en huertos de mango y limón: comparar la ET observada con la ETc esperada. Limitaciones: revisita irregular (órbita de la ISS), pocas escenas útiles. Acceso: AppEEARS.
>
> **Sentinel-2 (fase posterior):** vigor relativo de huertos (NDVI/NDRE, F3) y **verificación del historial declarado** (inundación de arroz, ciclos anuales vs cobertura perenne, desde 2017). No rellena el historial: muestra coincidencias o discrepancias.

**Regla de incorporación:** antes de agregar una variable, el equipo debe comprobar que (a) existe para San Lorenzo, (b) tiene cobertura temporal suficiente, (c) su resolución es compatible con el uso previsto y (d) sus unidades encajan en el cálculo.

## **7.2. Esenciales — NASA POWER**

**Por qué es la base:** entrega en un solo endpoint, sin autenticación, todas las variables para calcular ET0 (FAO-56) y GDD, con serie diaria desde 1981.

| Variable | Campo | Unidad | Uso |
| :---- | :---- | :---- | :---- |
| Temperatura máxima | `T2M_MAX` | °C | GDD, estrés térmico |
| Temperatura mínima | `T2M_MIN` | °C | GDD, frío nocturno |
| Temperatura media | `T2M` | °C | ET0 |
| Punto de rocío | `T2MDEW` | °C | ET0 (ea) |
| Humedad relativa | `RH2M` | % | Control de ea |
| Viento 2 m | `WS2M` | m/s | ET0 |
| Radiación solar | `ALLSKY_SFC_SW_DWN` | MJ/m²/día (**solo con `community=AG`**) | ET0 (Rn) |
| Presión | `PS` | kPa | Constante psicrométrica |
| Precipitación | `PRECTOTCORR` | mm/día | Control y relleno de IMERG |

> **Corrección v0.7 — unidades de radiación.** Según la comunidad solicitada, POWER puede devolver la radiación en kWh/m²/día en lugar de MJ/m²/día (factor 3,6). El adaptador **fija `community=AG`** y **valida la unidad leída del encabezado de la respuesta** antes de calcular; si no coincide, aborta. POR VERIFICAR en la primera descarga real.

**Petición tipo:**

```
GET https://power.larc.nasa.gov/api/temporal/daily/point
    ?parameters=T2M_MAX,T2M_MIN,T2M,T2MDEW,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PS,PRECTOTCORR
    &community=AG&latitude=-5.093608&longitude=-80.340280
    &start=19810101&end=20251231&format=JSON
```

Valores faltantes: `-999` → nulo, nunca cero.

**Limitación:** la meteorología proviene de MERRA-2 (~0,5° × 0,625°) y la radiación de CERES/GEWEX (~1°). Es serie de referencia, no microclima de parcela. Las mínimas nocturnas se suavizan: puede subestimarse el enfriamiento local (relevante para §9.6).

## **7.3. Complementarias**

### GPM IMERG

| Variable | Producto | Unidad | Uso |
| :---- | :---- | :---- | :---- |
| Precipitación diaria | `GPM_3IMERGDF` | mm/día | Balance y escenarios |
| Precipitación 30 min | `GPM_3IMERGHH` | mm/h | Intensidad de eventos |
| Calidad | `precipitationQualityIndex` | – | Filtro |

**Derivados:** acumulados, `RX1day`, `R95p`, `CDD`.
**Advertencia:** sobreestima lloviznas costeras. **Debe contrastarse con SENAMHI** y corregirse con factor documentado si el sesgo es sistemático.
**Latencia:** el producto *Final Run* llega con meses de retraso. Para F3 (semanas recientes) se usa *Late Run* o *Early Run*, etiquetado con su versión.
**Acceso rápido:** Giovanni (series de área en CSV, sin programar) o GES DISC.

### SMAP L4 — versión 8

| Variable | Producto | Unidad | Uso |
| :---- | :---- | :---- | :---- |
| Humedad superficial (0–5 cm) | `SPL4SMGP` v8 | m³/m³ | Condición superficial |
| Humedad de zona radicular (0–100 cm) | `SPL4SMGP` v8 | m³/m³ | Condición inicial del balance |
| Humedad de perfil | `sm_profile` | m³/m³ | Tendencia |

> **Corrección v0.6:** la v0.5 citaba la **versión 7**, retirada por NASA. La vigente es la **v8**: https://nsidc.org/data/spl4smgp/versions/8

**Advertencias:** es producto **modelado** (modelo de superficie asimilando observaciones), no sensor de parcela; celda de ~9 km; **no representa riego por gravedad**, por lo que subestima la humedad en valles irrigados. Uso en el MVP: solo como condición inicial en secano o en años de lluvia.
**Acceso:** AppEEARS (series por punto en CSV). **Verificar que AppEEARS sirva la versión 8** y no una anterior.

### SENAMHI, ENFEN, ANA y Junta de Usuarios

| Fuente | Variable | Uso | Verificación |
| :---- | :---- | :---- | :---- |
| SENAMHI — estación más cercana (p. ej. El Partidor, POR VERIFICAR) | P, Tmax, Tmin, HR | Validar IMERG y el sesgo de POWER en mínimas | Latencia, completitud |
| SENAMHI — pronóstico trimestral | Categorías de anomalía | pronosticado | Fecha de emisión, horizonte, probabilidad |
| ENFEN | ICEN mensual; comunicados oficiales | Clasificar años; etiqueta de campaña | Fecha de emisión |
| ANA | Volumen del reservorio San Lorenzo (hm³) | Contexto observado: percentil del volumen en la misma fecha | Capacidad total, útil y volumen muerto (POR VERIFICAR) |
| ANA | Caudal del río Quiroz (estación Zamba) | Recarga del reservorio; indicador adelantado | Serie, unidad (m³/s) |
| Junta de Usuarios San Lorenzo | **PCR**: área autorizada por cultivo y dotación (m³/ha) por campaña | Restricción de asignación (RT-06, RT-08) | Formato, comisión de regantes de la parcela |
| Junta / usuario | Calendario e intervalo de turnos (días) | Autonomía entre turnos (§9.5) | Comisión, campaña |

> NORTEX **no modela** cómo la Junta convierte el volumen del reservorio en dotaciones: **lee** el PCR publicado o declarado. Si el PCR aún no existe, muestra la dotación de la campaña histórica más parecida en volumen, etiquetada *escenario*.

## **7.4. Independencia de la evidencia (advertencia metodológica)**

**Los índices no son independientes.** Presentarlos como confirmaciones separadas infla la confianza artificialmente.

| Par de fuentes | Relación | Consecuencia |
|---|---|---|
| SMAP L4 ↔ SMAP L3 | L4 asimila L3: comparten información de origen | No contar como dos evidencias |
| ECOSTRESS ESI ↔ ECOSTRESS LST | ESI se deriva de ET, que usa LST y meteorología | Correlación alta por construcción |
| SPI ↔ SPEI | Comparten la serie de precipitación | Correlación alta |
| POWER ↔ IMERG (precipitación) | POWER también estima precipitación | No son independientes para lluvia |
| NDVI ↔ NDRE | Ambas derivan de la misma reflectancia | Correlación alta |

**Regla:** cuando dos indicadores comparten origen, se presentan como **un solo bloque de evidencia**, no como dos confirmaciones.

## **7.5. Fuentes descartadas como dato directo**

USDA Web Soil Survey, CropScape, PRISM, SSURGO, NAIP y OpenET **no aplican a Piura**. Se usan solo como referencia metodológica.

---

# **8. Contrato de variables**

## **8.1. Entrada**

| ID | Variable | Unidad | Fuente | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| V-01 | `tmax` | °C | POWER `T2M_MAX` | Esencial |
| V-02 | `tmin` | °C | POWER `T2M_MIN` | Esencial |
| V-03 | `tmean` | °C | POWER `T2M` | Esencial |
| V-04 | `dewpoint` | °C | POWER `T2MDEW` | Esencial |
| V-05 | `rh` | % | POWER `RH2M` | Esencial |
| V-06 | `wind_2m` | m/s | POWER `WS2M` | Esencial |
| V-07 | `solar_rad` | MJ/m²/día | POWER `ALLSKY_SFC_SW_DWN` | Esencial |
| V-08 | `pressure` | kPa | POWER `PS` | Esencial |
| V-09 | `precip_power` | mm/día | POWER `PRECTOTCORR` | Esencial |
| V-10 | `precip_daily` | mm/día | IMERG DF | Complementaria |
| V-11 | `precip_30min` | mm/h | IMERG HH | Complementaria |
| V-12 | `sm_surface` | m³/m³ | SMAP L4 v8 | Complementaria |
| V-13 | `sm_rootzone` | m³/m³ | SMAP L4 v8 | Complementaria |
| V-14 | `soil_texture` | categoría | Laboratorio / declarado | Esencial |
| V-15 | `soil_awc` | mm/mm | Laboratorio / SoilGrids | Esencial |
| V-16 | `soil_ph` | pH | Laboratorio | Esencial |
| V-17 | `soil_ec` | dS/m | Laboratorio | Esencial |
| V-18 | `soil_om` | % | Laboratorio | Esencial |
| V-19 | `irrigation_mm` | mm/campaña | ANA / Junta / usuario | **Esencial (v0.7)** |
| V-20 | `history_campaigns` | tabla | Usuario | Esencial |
| V-21 | `previous_crops` | lista | Historial | Esencial |
| V-22 | `parcel_geometry` | polígono | Dibujo manual | Esencial |
| V-23 | `field_area` | ha | Dibujo manual | Esencial |
| V-24 | `crop_id`, `sowing_date`, `stage` | catálogo; fecha; categoría | Usuario / fichas | Esencial |
| V-25 | `price_farmgate` | S/./kg | MIDAGRI / FAOSTAT | Esencial (referencia) |
| V-26 | `yield_reference` | t/ha | MIDAGRI / SIEA | Esencial (referencia) |
| V-27 | `cost_production` | S/./ha | MIDAGRI / SIEA | Esencial (referencia) |
| V-28 | `enfen_alert_state` | categoría | ENFEN (comunicado) | Esencial |
| V-29 | `reservoir_volume` | hm³ | ANA | **Esencial (v0.7)** |
| V-30 | `pcr_area_authorized` | ha por cultivo | Junta de Usuarios / declarado | **Esencial (v0.7)** |
| V-31 | `water_allocation` | m³/ha·campaña | PCR / Junta / declarado | **Esencial (v0.7)** |
| V-32 | `turn_interval` | días | Junta / declarado | **Esencial (v0.7)** |
| V-33 | `irrigation_system`, `application_efficiency` | categoría; adimensional | Declarado (gravedad ~0,5; goteo ~0,9 — POR VALIDAR) | **Esencial (v0.7)** |
| V-34 | `icen` | °C (anomalía) | ENFEN | **Esencial (v0.7)** |
| V-35 | `oni` | °C (anomalía) | NOAA | Complementaria |
| V-36 | `quiroz_flow` | m³/s | ANA, estación Zamba | Complementaria |
| V-37 | `water_ec` (ECw) | dS/m | Laboratorio / Junta | Complementaria (esencial para arroz → frutal) |
| V-38 | `water_table_depth` | m | Declarado / técnico | Complementaria (esencial para arroz → frutal) |
| V-39 | `soil_effective_depth` | m | Declarado / calicata | Complementaria |
| V-40 | `crop_variety` | categoría | Usuario | Esencial para perennes |
| V-41 | `t2m_hourly`, `rh2m_hourly` | °C, % | POWER horario | Complementaria (vigilancia de antracnosis, fase posterior) |

**Diferidas:** LST/ET/ESI (ECOSTRESS), NDRE/NDVI (Sentinel-2), aptitud GAEZ, SPEI, índices avanzados de sequía.

## **8.2. Derivadas**

| ID | Variable | Método | Estado |
| :---- | :---- | :---- | :---- |
| D-01 | `et0` | FAO-56 Penman-Monteith (§9.1) | ACORDADO |
| D-02 | `etc` | ET0 × Kc | ACORDADO |
| D-03 | `gdd_accum` | Σ max(0, (Tmax+Tmin)/2 − Tbase) | ACORDADO |
| D-04 | `heat_stress_days` | Tmax > umbral por etapa | POR VALIDAR |
| D-05 | `water_balance` | Balance FAO-56 en agotamiento con ETc,adj (§9.3) | ACORDADO (corregido v0.7) |
| D-06 | `depletion_dr` | Dr = (θ_FC − θ)·Zr (§9.3) | ACORDADO |
| D-07 | `spi_3`, `spi_6` | SPI con distribución mixta para ceros (§10.1) | ACORDADO, solo contexto |
| D-08 | `spei_3`, `spei_6` | SPEI correcto (§10.2) | **DIFERIDO (v0.7)** |
| D-09 | `cdd` | Días secos consecutivos | ACORDADO |
| D-10 | ~~`esan`~~ | Índice compuesto | **DIFERIDO** |
| D-11 | `gross_margin` | (rend × precio) − costo | ACORDADO |
| D-12 | `transition_flags` | RT-01 a RT-08 | ACORDADO |
| D-13 | `etc_adj` | Ks · Kc · ET0 (§9.3) | ACORDADO (v0.7) |
| D-14 | `water_coverage` | C = oferta asignada / demanda bruta (§9.4) | ACORDADO (v0.7) |
| D-15 | `autonomy_days`, `stress_days_between_turns` | RAW / ETc; intervalo − autonomía (§9.5) | ACORDADO (v0.7) |
| D-16 | `cool_nights` | Nº de días con Tmin < umbral, jun–ago (§9.6) | PROPUESTO (umbral POR VALIDAR) |
| D-17 | `reservoir_percentile` | Percentil del volumen respecto a la misma fecha en la serie histórica | ACORDADO (v0.7) |

---

# **9. Capa física**

## **9.1. ET0 — FAO-56 Penman-Monteith**

```
ET0 = [0.408·Δ·(Rn − G) + γ·(900/(T+273))·u2·(es − ea)]
      ─────────────────────────────────────────────────────
                 Δ + γ·(1 + 0.34·u2)

e°(T) = 0.6108·exp(17.27·T/(T+237.3))                 [kPa]
Δ     = 4098·e°(T) / (T+237.3)²                        [kPa/°C]
γ     = 0.000665·P                                     [kPa/°C], P en kPa
es    = [e°(Tmax) + e°(Tmin)]/2
ea    = e°(Tdew)
G     ≈ 0 (escala diaria)
```

> **Corrección v0.7:** la v0.6 escribía `Rn = Rns − Rnl` sin definir Rnl, que exige la radiación de cielo despejado (Rso) y, por tanto, la radiación extraterrestre (Ra). Sin estos términos el método no es auditable. Se completan con las ecuaciones FAO-56 (ec. 21–25, 37–39).

**Radiación (todas en MJ/m²/día):**

```
φ    = latitud en radianes  (−5.0936° → −0.08890 rad)
J    = día juliano (1…365/366)
dr   = 1 + 0.033·cos(2π·J/365)
δ    = 0.409·sin(2π·J/365 − 1.39)
ωs   = arccos(−tan φ · tan δ)
Ra   = (24·60/π)·0.0820·dr·[ωs·sin φ·sin δ + cos φ·cos δ·sin ωs]
Rso  = (0.75 + 2·10⁻⁵·z)·Ra                 z = altitud (68 m)
Rns  = (1 − 0.23)·Rs                        Rs = ALLSKY_SFC_SW_DWN
Rnl  = σ·[(Tmax,K⁴ + Tmin,K⁴)/2]·(0.34 − 0.14·√ea)·(1.35·Rs/Rso − 0.35)
       σ = 4.903·10⁻⁹ MJ/K⁴/m²/día ;  Rs/Rso acotado a ≤ 1
Rn   = Rns − Rnl
```

ET0 **se calcula, no se descarga**, para poder auditar el método. Versión del método: `ET0-FAO56-PM-v1`.

**Criterio de aceptación:** con los datos del **Ejemplo 18 de FAO-56** (cálculo diario), el resultado no difiere más de **±0,1 mm/día** del valor publicado. Prueba automatizada obligatoria antes de usar ET0 en el motor.

## **9.2. GDD y estrés térmico**

```
GDD_día  = max(0, ((Tmax + Tmin)/2) − Tbase)     con Tmax acotado a T_upper
GDD_acum = Σ GDD_día desde siembra o brotación
```

`Tbase` y `T_upper` por cultivo, desde ficha agronómica. El estrés térmico se cuenta **por etapa**.

> GDD sirve para los anuales (arroz, caupí, maíz). Para mango y limón, la etapa decisiva de la campaña es la **inducción floral y la floración**, que se evalúa con §9.6, no con GDD desde siembra.

## **9.3. Balance hídrico — revisión dimensional**

> **Corrección v0.6:** la v0.5 mezclaba profundidad radicular (m), humedad volumétrica (m³/m³) y agua almacenada (mm) sin declarar la conversión. Aquí se fija la convención.

**Convención única: todo el balance se expresa en milímetros de lámina de agua (mm).**

| Magnitud | Símbolo | Unidad | Conversión |
| :---- | :---- | :---- | :---- |
| Humedad volumétrica | θ | m³/m³ | adimensional |
| Profundidad radicular | Zr | mm | 1 m = 1000 mm |
| Agua almacenada | S | mm | **S = θ × Zr** |
| Capacidad de campo | θ_FC | m³/m³ | — |
| Punto de marchitez | θ_WP | m³/m³ | — |
| Agua disponible total | TAW | mm | **TAW = (θ_FC − θ_WP) × Zr** |
| Agotamiento | Dr | mm | **Dr = (θ_FC − θ) × Zr** |
| Agua fácilmente disponible | RAW | mm | **RAW = p × TAW** |

**Ecuaciones:**

```
TAW = (θ_FC − θ_WP) · Zr                [mm]
Dr  = (θ_FC − θ) · Zr                   [mm]
RAW = p · TAW                           [mm]
Ks  = (TAW − Dr) / ((1 − p) · TAW)      [adimensional], si Dr > RAW
Ks  = 1                                 si Dr ≤ RAW
ETc,adj = Ks · Kc · ET0                 [mm/día]   (= ETa)
```

> **Corrección v0.7:** la v0.6 escribía `ΔS = P_eff + I − ETc − R − D − DP`. Restar **ETc** cuando el suelo está agotado extrae más agua de la que el cultivo puede tomar, y `D` y `DP` no estaban diferenciados. Se adopta la **forma FAO-56 (ec. 85) en agotamiento**, con ETc,adj.

**Ecuación diaria del balance (única en todo el documento; D-05 la referencia):**

```
Dr,i = Dr,i−1 − (P − RO)i − Ii − CRi + ETc,adj,i + DPi        [mm]

con la restricción     0 ≤ Dr,i ≤ TAW
DPi  = max(0, (P − RO)i + Ii − ETc,adj,i − Dr,i−1)            [mm]  (percolación cuando se supera capacidad de campo)
CRi  = 0  salvo dato de napa freática somera (V-38)
```

| Término | Significado | Fuente |
| :---- | :---- | :---- |
| P | Precipitación diaria | IMERG o POWER `PRECTOTCORR` (modelado) |
| RO | Escorrentía superficial | 0 en MVP salvo eventos extremos; declarar el supuesto |
| I | Riego **neto** aplicado = riego bruto × eficiencia (V-33) | Declarado / turnos |
| CR | Ascenso capilar | 0 salvo napa declarada |
| DP | Percolación profunda | Calculada |
| ETc,adj | Evapotranspiración real del cultivo | Calculada |

**Cierre de masa (prueba obligatoria):** en todo periodo, `Σ(P − RO) + ΣI + ΣCR − ΣETc,adj − ΣDP = Dr,inicio − Dr,fin`, con tolerancia ±0,1 mm.

**Verificación de unidades:**

| Término | Unidad | Correcto |
| :---- | :---- | :---: |
| θ × Zr | (m³/m³) × mm = mm | ✅ |
| TAW | (m³/m³) × mm = mm | ✅ |
| ETc,adj = Ks × Kc × ET0 | (–) × (–) × mm/día = mm/día | ✅ |
| Dr acumulado en el periodo | mm/día × día = mm | ✅ |
| Riego: 1 mm sobre 1 ha | 10 m³ | ✅ |

**Conversión desde SMAP:** SMAP entrega θ en m³/m³. Para usarlo en el balance:

```
Dr,0 (mm) = (θ_FC − θ_SMAP) × Zr (mm)
```

Y solo se usa como **condición inicial**, no como serie pronosticada, y solo en secano o en años de lluvia (no ve el riego).

## **9.4. Cobertura hídrica de la campaña (nuevo v0.7)**

Compara **en m³** lo que el cultivo necesita con lo que la Junta asigna. No es un índice: es un cociente de dos magnitudes físicas con la misma unidad.

```
DN    = Σ (ETc,adj − P_eff)                  [mm]   demanda neta de la campaña, por escenario (P10/P50/P90)
DB    = DN / Ea                              [mm]   demanda bruta; Ea = eficiencia de aplicación (V-33)
DB_m3 = DB × 10 × área_ha                    [m³]
O     = dotación (V-31) × área_ha            [m³]   oferta asignada por el PCR
C     = O / DB_m3                            [adimensional]
```

| Resultado | Etiqueta en pantalla | Respuesta del motor |
| :---- | :---- | :---- |
| C ≥ 1 en P50 y en P10 | Cubierto | Sin restricción hídrica |
| C ≥ 1 en P50 y C < 1 en P10 | Vulnerable | Advertencia en la etapa crítica |
| C < 1 en P50 | No cubierto | "No viable con la dotación declarada" (RT-06) |
| Área no autorizada en el PCR | No autorizado | "No viable por asignación" (RT-08) |
| Sin dotación | Por determinar | EX-04 |

Categoría del resultado: **simulado** (combina escenario + declarado).

## **9.5. Autonomía entre turnos de riego (nuevo v0.7)**

NORTEX no fija los turnos (los fija la Junta). Responde lo que el agricultor sí controla: **¿mi suelo aguanta hasta el próximo turno?**

```
Autonomía (días)      = RAW / ETc,diaria = p·(θ_FC − θ_WP)·Zr / (Kc·ET0)
Días de estrés        = max(0, intervalo_entre_turnos − Autonomía)
```

| Ejemplo ilustrativo (valores POR VALIDAR) | Arenoso | Franco |
| :---- | :---- | :---- |
| θ_FC − θ_WP | 0,08 | 0,16 |
| Zr (mango) | 1 200 mm | 1 200 mm |
| p | 0,5 | 0,5 |
| RAW | 48 mm | 96 mm |
| ETc (Kc 0,8 × ET0 5 mm/día) | 4 mm/día | 4 mm/día |
| **Autonomía** | **12 días** | **24 días** |

Explica con física simple por qué el mismo turno funciona en un suelo franco y falla en uno arenoso. Se usa en F1/F2 (por escenario) y en F3 (con ET0 reciente).

## **9.6. Noches frescas para la inducción floral del mango (nuevo v0.7)**

**Por qué:** en Piura la floración del mango depende de un invierno fresco (y/o de estrés hídrico controlado). Un invierno cálido —típico de El Niño Costero— puede hacer fallar la inducción floral y comprometer la campaña **meses antes de cualquier lluvia**. POR VERIFICAR: la caída de producción de mango de Piura en 2023-24 se atribuyó en buena parte a este fenómeno.

```
cool_nights(t) = Σ [T2M_MIN(d) < T_ind]    para d entre el 1 de junio y la fecha t (hasta el 31 de agosto)
T_ind          = umbral de inducción por variedad (p. ej. ~15–17 °C), POR VALIDAR con INIA / ficha Kent
```

| Salida | Categoría |
| :---- | :---- |
| "Este invierno lleva N noches frescas" | modelado (POWER) |
| "La mediana 1991–2020 a esta fecha es M; está en el percentil k" | escenario |
| "Años análogos El Niño Costero: …" | escenario |

**Lo que NO se afirma:** no se calcula "probabilidad de floración" ni rendimiento. Es una variable contada, con umbral declarado, que se compara con el propio histórico.
**Advertencia:** POWER (~50 km) suaviza las mínimas; si hay estación SENAMHI cercana, se contrasta y se declara el sesgo.

---

# **10. Sequía**

> **Cambio de prioridad v0.7:** en San Lorenzo la sequía que decide la campaña es hidrológica y operativa (§7.1). SPI queda como **contexto** (útil sobre todo para describir años El Niño o parcelas en secano); SPEI se **difiere**. Los indicadores que mandan son la cobertura hídrica (§9.4), la autonomía entre turnos (§9.5) y el percentil del volumen del reservorio (§10.3).

## **10.1. SPI — precipitación (con tratamiento de ceros)**

> **Corrección v0.7:** en la costa de Piura hay muchos meses —y trimestres— con lluvia cero. La gamma no está definida en cero, así que el procedimiento de la v0.6 producía un índice inválido. Se adopta la **distribución mixta** estándar.

```
1. Agregar P en ventanas de k meses (k = 3, 6), por mes calendario de cierre
2. q = fracción de valores P_k = 0 en la serie histórica de ese mes
3. Ajustar una gamma G(x) solo a los valores P_k > 0
4. H(x) = q + (1 − q)·G(x)
5. SPI = Φ⁻¹(H(P_k))
```

**Reglas adicionales:**
- Si **q > 0,5** para un mes de cierre, el SPI de ese mes **no se reporta**: el índice no informa nada en un régimen casi siempre seco. Se muestra "no aplicable: estación seca".
- Mínimo de 30 años de serie para el ajuste; si no, EX-06.

Clasificación (McKee et al., 1993):

| SPI | Categoría |
| :---- | :---- |
| > 2,0 | Extremadamente húmedo |
| 1,5 a 2,0 | Muy húmedo |
| 1,0 a 1,5 | Moderadamente húmedo |
| −1,0 a 1,0 | Normal |
| −1,5 a −1,0 | Moderadamente seco |
| −2,0 a −1,5 | Severamente seco |
| < −2,0 | Extremadamente seco |

## **10.2. SPEI — definición correcta**

> **Corrección v0.6:** la v0.5 lo describía como "SPI sobre P − ET0". **Eso es incorrecto.** SPEI no es un SPI aplicado a una serie distinta: usa un **balance climático acumulado** y un **procedimiento de estandarización propio**.

**Procedimiento correcto (Vicente-Serrano et al., 2010):**

```
1. Balance climático mensual:      D_i = P_i − PET_i
2. Acumulación en k meses:         D_k = Σ D_i  (i = t−k+1 … t)
3. Ajuste a distribución
   log-logística de 3 parámetros   (no gamma)
4. Estimación de parámetros por L-moments o máxima verosimilitud
5. Transformación a normal:        SPEI = Φ⁻¹(F(D_k))
```

**Diferencias que importan:**

| Aspecto | SPI | SPEI |
| :---- | :---- | :---- |
| Variable | Precipitación | Balance P − PET |
| Distribución | Gamma (2 parámetros) | Log-logística (3 parámetros) |
| PET | No usa | **Sí, y su método importa** |
| Uso | Sequía meteorológica | Sequía agroclimática |

**Decisión pendiente (POR VALIDAR):** qué método de PET usar dentro del SPEI (Thornthwaite vs Penman-Monteith). Cambia los resultados. Debe declararse y fijarse en la versión del método.

**Estado v0.7: DIFERIDO.** Además de la decisión sobre PET, en un régimen hiperárido el balance P − PET es casi siempre muy negativo y el índice aporta poco a la decisión de una parcela regada. Se retoma solo si el equipo decide atender parcelas en secano.

## **10.3. Otros indicadores**

| Indicador | Qué mide | Fuente | Estado |
| :---- | :---- | :---- | :---- |
| **Percentil del volumen del reservorio** (D-17) | Sequía hidrológica | ANA | **ACORDADO, esencial (v0.7)** |
| **Cobertura hídrica C** (D-14) | Sequía operativa (asignación vs demanda) | Balance + PCR | **ACORDADO, esencial (v0.7)** |
| **Días de estrés entre turnos** (D-15) | Sequía agronómica por turnado | Balance + turnos | **ACORDADO, esencial (v0.7)** |
| **ETa/ETc** | Sequía agronómica | Balance | ACORDADO |
| **Caudal del río Quiroz** | Recarga del sistema | ANA | Complementaria |
| **CDD** | Días secos consecutivos | IMERG | Contexto |
| **Percentil SMAP** | Sequía edáfica regional | SMAP L4 v8 | Contexto, con advertencia (no ve riego) |

### **10.3.1. Ajuste del motor según régimen**

| Aspecto | **Estiaje** (volumen bajo, La Niña o neutro seco) | **Exceso** (El Niño Costero con lluvias) |
| :---- | :---- | :---- |
| Restricción dominante | Dotación (C < 1), área no autorizada en PCR | Drenaje, anegamiento, acceso a la parcela |
| Término del balance que domina | I limitado → Dr crece → Ks < 1 | P y RO altos, DP alto, suelo saturado |
| Arroz | Riesgo de no autorización | Riesgo bajo (tolera anegamiento) |
| Caupí / maíz | Estrés en floración | Pudriciones, encharcamiento: **alto** |
| Mango | Estrés en llenado de fruto | **Falla de inducción floral por invierno cálido (§9.6)**, antracnosis, mosca de la fruta |
| Limón sutil | Caída de flor y fruto; salinidad por menos lavado | ***Phytophthora*** por asfixia radicular |
| Fuentes que ganan peso | ANA / Junta, POWER (ET0 alta) | IMERG (intensidad, RX1day), ENFEN, SMAP |

## **10.4. ESAN — diferido**

> **Corrección v0.6:** el índice compuesto ESAN **sale del MVP**.

Razones:
1. Su normalización no estaba definida con precisión (rango, dirección, tratamiento de valores atípicos).
2. Sus pesos no tenían justificación ni calibración.
3. Un índice compuesto sin validación **no debe clasificar sequías reales**.

**Qué se hace en su lugar:** se presentan los indicadores **por separado** (SPI, SPEI, CDD, percentil SMAP, ETa/ETc) y se deja que el usuario y el técnico los interpreten. Si en el futuro se retoma ESAN, requiere: definición formal, pesos declarados, validación contra eventos históricos y versión del método.

## **10.5. ENSO — formulación corregida**

> **Corrección v0.6:** la v0.5 afirmaba que en Piura "la sequía se asocia a La Niña, no a El Niño". Esa formulación era demasiado categórica.

**Formulación correcta:**

- En Piura, **El Niño Costero** se asocia con **mayor probabilidad de lluvias extremas**.
- **La Niña** se asocia con **mayor probabilidad de déficit hídrico**.
- **Pero no es determinista.** SENAMHI documenta también escenarios de sequía en años El Niño, y la respuesta depende de la intensidad, la duración y la posición del calentamiento.
- Por lo tanto, NORTEX **no traduce el estado ENFEN en una predicción**. Lo usa para (a) etiquetar la campaña y (b) estratificar la muestra histórica con el **ICEN**, con las advertencias de §6.3.
- El impacto de El Niño Costero en Piura **no se limita a la lluvia**: incluye invierno cálido (§9.6), drenaje y sanidad (§10.3.1).

---

# **11. Parcela: dibujo manual en el mapa**

> **Cambio v0.6:** se retira el levantamiento GPS del MVP. El motivo es correcto: consume tiempo de desarrollo, depende de hardware, batería y señal, y no es lo que se está evaluando.

## **11.1. Flujo**

1. El usuario abre el mapa y pulsa "Dibujar mi parcela".
2. Toca el mapa para añadir vértices; la línea se cierra automáticamente al tocar el primero.
3. Puede arrastrar vértices, insertar nuevos o deshacer el último.
4. El sistema calcula área y perímetro **en UTM 17S**.
5. El usuario nombra la parcela y confirma.
6. Se guarda como versión 1, con opción de exportar a GeoJSON o KML.

## **11.2. Validaciones**

| Regla | Valor |
| :---- | :---- |
| Vértices mínimos | 3 |
| Área mínima | 0,1 ha |
| Autointersección | Rechazada con el tramo resaltado |
| Fuera de la zona de estudio | Advertencia, no bloqueo |
| Área declarada vs dibujada | Si difieren > 20 %, pedir confirmación |

## **11.3. Regla de escala efectiva (obligatoria en pantalla)**

| Dato | Resolución | Qué se puede afirmar |
| :---- | :---- | :---- |
| Polígono dibujado | ~10–30 m (precisión del mapa) | Límites y área aproximada |
| POWER meteorología / radiación | ~0,5° × 0,625° / ~1° | Clima de referencia regional |
| IMERG | ~11 km | Lluvia regional |
| SMAP | ~9 km | Humedad regional |
| Reservorio / PCR | Sistema de riego / comisión | Disponibilidad del sistema, no de la parcela |
| ECOSTRESS (fase posterior) | ~70 m | Estado del huerto, en fechas de paso |
| Sentinel-2 (fase posterior) | 10–20 m | Vigor relativo dentro de la parcela |

**Nunca se presenta un dato de 9 km como si fuera de la parcela.** El sistema muestra la resolución junto a cada cifra.

## **11.4. Diferido**

Levantamiento con GPS móvil, subdivisión por cuarteles con recorrido, sincronización offline. Se documenta como mejora futura.

---

# **12. Historial de la finca**

```
Finca → Parcela → Campaña → Cultivo / Labores / Resultado / Eventos
```

| Uso | Cómo se aprovecha |
| :---- | :---- |
| Calibrar Kc y rendimiento | Sustituir literatura por datos del propio campo |
| Evaluar transición | La secuencia histórica es el punto de partida de F2 |
| Normalizar índices | Comparar contra el historial, no contra un promedio global |
| Validar el motor | Backtesting de evaluaciones pasadas |
| Explicar | "Esto se basa en sus últimas 4 campañas" |

**Regla de oro:** el historial no se inventa ni se rellena. Si falta un año, se muestra el hueco y la fundamentación baja a "limitada".

---

# **13. ETL y trazabilidad**

1. **Extraer** por producto y versión, para la ubicación y fechas solicitadas.
2. **Verificar** esquema, unidades, calendario, coordenadas, ausentes y banderas.
3. **Normalizar** unidades y fechas. Nunca mezclar mm/h con mm/día.
4. **Relacionar** solo variables compatibles; etiquetar lo regional como regional.
5. **Derivar** ET0, GDD, noches frescas, balance, cobertura hídrica, autonomía, SPI, índices de extremo.
6. **Evaluar** escenarios, restricciones y transiciones.
7. **Explicar** entradas, motivos y vacíos.

**Metadatos mínimos:** producto, organismo, versión, fecha de referencia, fecha de consulta, unidad, ubicación, resolución y `data_category` con **uno de los seis valores de §6.1**: observado / modelado / pronosticado / escenario / simulado / declarado.

**Eficiencia (ISO/IEC 25010):** las series POWER 1981–2025 y los escenarios por ventana se **precalculan** en el ETL y se guardan en caché local (Parquet o SQLite). La interfaz no consulta APIs externas durante la evaluación. Meta: respuesta de F1/F2 < 2 s.

---

# **14. Motor de decisiones**

| Subcomponente | Entrada | Salida |
| :---- | :---- | :---- |
| **A. Riesgo por escenario** (físico-agroclimático e hídrico) | POWER, IMERG, SMAP, ANA, PCR, turnos, ICEN | ET0, GDD, noches frescas, balance, cobertura hídrica, autonomía, extremos |
| **B. Fenológico** | Cultivo, variedad, siembra o etapa, Kc, umbrales | Etapas y demanda; inducción floral en perennes |
| **C. Restricciones y transición** | Suelo, ECw, napa, agua asignada, historial, GAEZ (señal) | Viabilidad |
| **D. Económico** | Precios, rendimientos, costos | Margen y sensibilidad |
| **E. Explicación** | Resultados A–D | Alternativas, motivos y vacíos |

## **14.1. Pseudoflujo**

```
evaluar(cultivo, ventana, parcela, historial, escenario):
  validar entradas
  → recuperar historial y estado actual
  → filtros duros (suelo, área autorizada en PCR, transición)
  → señales de aptitud (GAEZ: advertencia, no exclusión)
  → proyectar etapas (GDD en anuales / calendario fenológico e inducción floral en perennes)
  → calcular ET0 → Kc·ET0 → balance FAO-56 → Dr/Ks → ETc,adj
  → cobertura hídrica C por escenario; autonomía entre turnos
  → contexto: percentil del reservorio, SPI (si aplica), CDD
  → riesgo por etapa × escenario
  → margen económico
  → suficiencia de evidencia
  → devolver resultado explicable
```

F1 lo ejecuta para varias ventanas con el mismo cultivo.
F2 lo ejecuta para varios cultivos en la misma ventana y compara transiciones.
F3 lo repite para los periodos restantes de un cultivo establecido.

## **14.2. Qué NO debe hacer el motor**

- Confundir un escenario construido con un pronóstico oficial.
- Recomendar caudales de riego o dosis de fertilización sin datos locales.
- **Descartar un cultivo solo porque GAEZ lo clasifique como no apto.**
- Descartar una rotación por un campo desconocido: usar "por determinar".
- Atribuir mejoras de fertilidad o rendimiento a porcentajes arbitrarios.
- Tratar mango o limón como cultivo anual.
- Presentar una celda de 9 km como medición de parcela.
- Convertir una alerta ENFEN en una predicción de milímetros.
- Usar ESAN para clasificar sequías.
- Calcular un "score de resiliencia" u otro índice agregado sin fórmula, pesos y validación.
- Presentar como predicción un resultado de modelo estadístico o de ML no validado.
- Restar ETc (en lugar de ETc,adj) en el balance cuando el suelo está agotado.
- Reportar SPI en meses donde más de la mitad de la serie es lluvia cero.

## **14.3. Trazabilidad variable → función**

| Variable | F1 | F2 | F3 |
| :---- | :---: | :---: | :---: |
| Tmax / Tmin | ● | ● | ● |
| Radiación, viento | ● | ● | ○ |
| ET0 / ETc | ● | ● | ● |
| Precipitación IMERG | ● | ● | ● |
| SMAP (condición inicial, secano / lluvia) | ○ | ○ | ○ |
| SPI (contexto) | ○ | ○ | ○ |
| Historial | ● | ● | ● |
| Suelo declarado | ● | ● | ○ |
| Precios / costos | ○ | ● | ○ |
| ENFEN / ICEN | ● | ● | ● |
| Reservorio, PCR, dotación | ● | ● | ● |
| Intervalo de turnos | ● | ● | ● |
| Noches frescas (mango) | ● | ● | ● |
| ECw, napa | ○ | ● | ○ |

---

# **15. Interfaces**

| Pantalla | Contenido |
| :---- | :---- |
| **Mi parcela** | Mapa con polígono dibujado, superficie, suelo y agua declarados |
| **Historial** | Línea de tiempo de campañas |
| **¿Cuándo sembrar? (F1)** | Calendario de ventanas, GDD, riesgos por etapa |
| **¿Qué sembrar? (F2)** | Cultivos y transición desde el historial |
| **Ya sembré (F3)** | Etapa, estrés, sequía, riesgos del periodo |
| **Detalle** | Cuatro dimensiones, razones, datos faltantes |
| **Ficha de preparación** | Ítems verificables ✔ / ✘ / desconocido: análisis de suelo vigente, dotación confirmada, intervalo de turnos conocido, sistema de riego, ECw conocida, historial completo, variedad declarada. **Sin suma ni ponderación.** |
| **Estado de datos** | Fuente, fecha, resolución y categoría del dato |

**Ejemplo de salida (ficticio):** "Para la ventana evaluada, el frijol caupí no presenta incompatibilidad confirmada con el suelo declarado. Con la dotación declarada, la cobertura hídrica es suficiente en el escenario medio (P50) pero no en el seco (P10 de 1991–2020): advertencia en floración. Su suelo arenoso aguanta unos 9 días entre riegos y el turno es cada 14: se prevén 5 días de estrés por turno (simulado). El reservorio está en el percentil 30 para esta fecha (observado, ANA)."

**Alerta liviana (demo, fase posterior para envío real):** texto ≤ 160 caracteres, con qué, por qué, categoría y fecha. En el MVP se genera el texto y un enlace `wa.me` prellenado; no se integra API de mensajería.

```
NORTEX 14/11: su suelo aguanta ~12 días sin riego; próximo turno en 16. Riesgo de estrés (simulado). Fuente: POWER + suelo declarado.
```

---

# **16. Arquitectura**

| Módulo | Responsabilidad |
| :---- | :---- |
| Frontend web | Dibujo de parcela, calendarios, comparaciones |
| Servicio de parcelas | Polígono, superficie, suelo, agua |
| Servicio de historial | Campañas, labores, resultados, eventos |
| Adaptadores de fuentes | POWER, IMERG, SMAP, SENAMHI, ENFEN, ANA, Junta (PCR), SIEA/MIDAGRI, FAOSTAT — contrato común por adaptador |
| ETL y caché | Validación, normalización, reproducibilidad; precálculo de series y escenarios |
| Catálogo agronómico | Arroz, caupí, maíz, mango, limón sutil (JSON con fuente y estado por parámetro) |
| Motor físico | ET0, GDD, noches frescas, balance, cobertura, autonomía, SPI — módulo puro sin I/O, versionado y con pruebas |
| Motor de evaluación | Restricciones, transición, economía |
| Servicio de explicaciones | Causas, límites y campos faltantes |

---

# **17. Requerimientos**

## **17.1. Funcionales**

| ID | Requerimiento |
| :---- | :---- |
| RF-01 | Dibujar, editar y guardar el polígono de la parcela en el mapa. |
| RF-02 | Calcular área y perímetro en UTM 17S. |
| RF-03 | Registrar campañas, cultivos, labores, rendimientos y eventos. |
| RF-04 | Marcar datos desconocidos sin sustituirlos. |
| RF-05 | Cargar POWER (`community=AG`) con metadatos, fecha, unidad validada y categoría del dato. |
| RF-06 | Calcular ET0 por FAO-56 (con Ra, Rso, Rnl) con versión del método. |
| RF-07 | Calcular GDD y días de estrés térmico por etapa. |
| RF-08 | Cargar IMERG y calcular acumulados, RX1day, R95p y CDD. |
| RF-09 | Calcular SPI-3 y SPI-6 con distribución mixta para ceros; no reportarlo si q > 0,5. |
| RF-10 | ~~Calcular SPEI-3 y SPEI-6~~ — **DIFERIDO (v0.7)**. |
| RF-11 | Cargar SMAP L4 **v8** y convertir θ a Dr inicial (mm) usando Zr. |
| RF-12 | Construir escenarios P10/P50/P90 con año análogo; años ENSO con menos de 10 casos como análogos individuales. |
| RF-13 | Mostrar la categoría del dato con uno de los seis valores de §6.1. |
| RF-14 | Evaluar ventanas de siembra de un cultivo (F1). |
| RF-15 | Comparar cultivos y transiciones desde el historial (F2). |
| RF-16 | Registrar cultivo establecido y evaluar riesgo por etapa (F3). |
| RF-17a | Mostrar la **viabilidad** de cada alternativa. |
| RF-17b | Mostrar el **riesgo** por etapa y escenario de cada alternativa. |
| RF-17c | Mostrar la **conveniencia** (margen bruto) de cada alternativa. |
| RF-17d | Mostrar la **fundamentación** (suficiencia de evidencia) de cada alternativa. |
| RF-18 | Estimar margen bruto con datos MIDAGRI/FAOSTAT y sobreescritura del usuario. |
| RF-19 | Guardar evaluación reproducible con fecha, fuentes y versión de modelo. |
| RF-20 | Mostrar resolución de cada variable junto a su valor. |
| RF-21 | Advertir el compromiso de 20 años al proponer un perenne. |
| RF-22 | Mostrar GAEZ como señal de aptitud, no como exclusión. |
| RF-23 | Registrar volumen del reservorio, PCR (área autorizada y dotación) e intervalo de turnos, por entrada manual si no hay API. |
| RF-24 | Calcular la cobertura hídrica C por cultivo y escenario (§9.4). |
| RF-25 | Calcular la autonomía entre turnos y los días de estrés previstos (§9.5). |
| RF-26 | Calcular las noches frescas del invierno para mango y compararlas con el histórico (§9.6). |
| RF-27 | Clasificar los años históricos por ICEN y mostrar comunicados ENFEN en paralelo con los escenarios. |
| RF-28 | Mostrar la ficha de preparación de la campaña sin agregación numérica. |
| RF-29 | Generar el texto de alerta liviana (≤ 160 caracteres) con categoría y fecha. |

## **17.2. No funcionales**

| ID | Criterio |
| :---- | :---- |
| RNF-01 | Uso en campo verificable: tipografía ≥ 16 px, alto contraste al sol; **5 agricultores completan F1 sin ayuda en menos de 5 minutos**. |
| RNF-08 | Respuesta de F1/F2 en menos de 2 s con datos en caché (sin llamadas externas durante la evaluación). |
| RNF-09 | Modo degradado sin conexión: consulta de evaluaciones guardadas con fecha del último dato. |
| RNF-02 | Identificar siempre la categoría del dato. |
| RNF-03 | Ante fallo de API, mostrar fecha del último dato; nunca datos viejos como actuales. |
| RNF-04 | Conservar unidades, fecha, producto/versión y reglas de evaluación. |
| RNF-05 | Probar con datos faltantes, suelo salino, riego insuficiente y parcelas pequeñas. |
| RNF-06 | Proteger datos de parcela. |
| RNF-07 | Toda variable espacial declara resolución y advertencia de escala. |

## **17.3. Especificación y criterios de aceptación (ISO/IEC/IEEE 29148)**

Cada requisito debe ser **necesario, inequívoco, verificable, singular, factible y trazable**. Los requisitos del MVP se especifican con esta plantilla; abajo, los que bloquean el motor. La calidad del producto se organiza según **ISO/IEC 25010:2023** (adecuación funcional, eficiencia, capacidad de interacción, fiabilidad, mantenibilidad, portabilidad, seguridad y *safety*).

| ID | Enunciado ("el sistema deberá…") | Criterio de aceptación | Verificación | Trazabilidad |
| :---- | :---- | :---- | :---- | :---- |
| RF-05 | …rechazar una respuesta POWER cuya unidad de radiación no sea MJ/m²/día | Una respuesta con kWh/m²/día produce error explícito, no un cálculo | Prueba automatizada con respuesta simulada | V-07 → D-01 |
| RF-06 | …calcular ET0 FAO-56 PM diaria | Ejemplo 18 de FAO-56: diferencia ≤ 0,1 mm/día | Prueba automatizada | V-01…V-08 → D-01 → D-02, D-05 |
| RF-09 | …calcular SPI con distribución mixta | Serie sintética con 40 % de ceros: el SPI de un valor cero coincide con la convención declarada (p. ej. Φ⁻¹(q/2)); con 60 % de ceros, no se reporta | Prueba automatizada | V-09/V-10 → D-07 |
| D-05 | …cerrar el balance de masa | Σ entradas − Σ salidas = ΔDr ± 0,1 mm en toda la campaña; 0 ≤ Dr ≤ TAW siempre | Prueba automatizada | D-05 → D-14, D-15 |
| RF-24 | …calcular C en m³ | Caso manual: DN 600 mm, Ea 0,5, 1 ha, dotación 10 000 m³/ha → C = 10 000 / 12 000 = 0,83 → "No cubierto" | Prueba automatizada | V-31, V-33 → D-14 → RT-06 |
| RF-25 | …calcular la autonomía | Caso del ejemplo arenoso de §9.5 → 12 días | Prueba automatizada | V-15, V-32 → D-15 |
| RF-13 | …etiquetar cada cifra | Ninguna cifra en pantalla sin `data_category` | Revisión de interfaz + prueba de esquema | Todas |

> Nota sobre RF-09: la convención exacta para el valor de SPI cuando P = 0 (p. ej. usar H(0) = q o el punto medio q/2) debe **declararse en la versión del método**; la prueba verifica la convención elegida.

---

# **18. Excepciones**

| ID | Situación | Respuesta |
| :---- | :---- | :---- |
| EX-01 | Polígono inválido | Rechazar y resaltar el tramo |
| EX-02 | Parcela < 0,1 ha | Advertir que la incertidumbre domina |
| EX-03 | Sin análisis de suelo | Usar SoilGrids, marcar "dato global" |
| EX-04 | Sin dotación de riego confirmada | Resultado "por determinar" en opciones dependientes de agua |
| EX-05 | API caída | Backoff, caché y aviso de antigüedad |
| EX-06 | Serie histórica < 15 años | Degradar confianza del escenario |
| EX-07 | Categoría ENSO con < 10 años | No calcular percentiles condicionados; mostrar años análogos individuales |
| EX-08 | GAEZ clasifica como no apto | Advertencia, no exclusión |
| EX-09 | Perenne propuesto | Advertir 3–4 años sin ingreso y compromiso de 20 años |
| EX-10 | Historial con huecos | Fundamentación limitada, no rellenar |
| EX-11 | Precio no disponible | FAOSTAT o entrada manual |
| EX-12 | Pronóstico caducado | Marcar como vencido |
| EX-14 | Unidad de POWER inesperada | Abortar el cálculo y registrar el error; nunca convertir en silencio |
| EX-15 | PCR de la campaña aún no publicado | Usar dotación de la campaña análoga en volumen, etiquetada *escenario* |
| EX-16 | Intervalo de turnos desconocido | Autonomía calculada; días de estrés "por determinar" |
| EX-17 | Mes de SPI con q > 0,5 | "No aplicable: estación seca" |
| EX-18 | Variedad de mango no declarada | Umbral de noches frescas genérico, marcado "por validar" |
| EX-13 | Resultados degenerados | Avisar que los criterios no discriminan |

---

# **19. Verificación con datos reales**

> Esta sección es la más importante del documento: **nada de lo anterior está integrado**. Antes de construir el motor definitivo, deben revisarse muestras reales.

| Muestra | Revisión práctica | Decisión posterior |
| :---- | :---- | :---- |
| POWER diario, 1981–2025, punto piloto, `community=AG` | Nombres, **unidad de radiación**, ausentes (`-999`), fechas, coherencia Tmax > Tmin, inicio de la serie de radiación | Esquema del adaptador |
| ICEN (ENFEN) | Serie mensual, años El Niño Costero / La Niña desde 1981 | Lista de años análogos |
| PCR de campañas recientes (Junta) | Área autorizada por cultivo, dotación m³/ha, comisión | ¿Entrada manual o tabla histórica? |
| Volumen del reservorio (ANA) | Serie, capacidad total y útil, volumen muerto | Percentil por fecha |
| IMERG diario, misma ventana | ¿Tasa o acumulado? Versión; sesgo vs SENAMHI | ¿Corrección escalar? |
| SMAP L4 **v8**, 12 meses | Nombres reales, unidades, máscara, celda asignada | ¿Aporta o se descarta? |
| Análisis de suelo, anonimizado | Parámetros, unidades, fecha, profundidad, método | Campos de suelo evaluables |
| SENAMHI, estación cercana | Latencia, completitud, comparabilidad | ¿Valida IMERG? |
| ANA / Junta, reporte de agua | Formato, fecha, cobertura, relación con turnos | ¿Integrar o pedir manual? |
| MIDAGRI / SIEA, Piura | Unidad monetaria, campaña, fuente | Base económica |
| Fichas INIA | Ciclo, Kc, Tbase, umbrales por cultivo | Sustituir rangos indicativos |
| ECOSTRESS (fase posterior) | Nº de escenas útiles sobre Piura | ¿Viable o solo ejemplo? |
| Sentinel-2 (fase posterior) | Nubosidad, saturación | ¿Indicador relativo? |

**Criterio de descarte:** una variable se pospone si no responde a ninguna decisión del MVP, repite información sin ventaja, tiene resolución incompatible o presenta huecos inviables.

---

# **20. Alcance del MVP**

## **20.1. El recorte**

> **La v0.5 prometía demasiado para 48 horas.** El MVP se reduce a **un flujo de extremo a extremo** que funcione con datos reales.

**Flujo único:**

```
1. El agricultor dibuja su parcela en el mapa
2. Declara suelo, sistema de riego, dotación, intervalo de turnos e historial básico
3. Elige un cultivo (p. ej. caupí o mango) y una ventana de siembra o campaña
4. Recibe: viabilidad · riesgo · conveniencia · fundamentación
   (incluye cobertura hídrica, autonomía entre turnos y, para mango, noches frescas)
5. Cada cifra muestra fuente, fecha y categoría
```

**Criterio de "MVP terminado":** el flujo funciona de punta a punta con datos POWER reales; ET0 y el balance pasan sus pruebas (§17.3); si falta la dotación, el resultado dice "por determinar" y no inventa.

## **20.2. Qué entra y qué no**

| Elemento | MVP | Fase posterior |
| :---- | :---: | :---: |
| Dibujo manual de parcela | ✅ | |
| Historial (3 campañas) | ✅ | |
| POWER + ET0 + GDD | ✅ | |
| Noches frescas (mango) | ✅ | |
| Escenarios P10/P50/P90 + años análogos ICEN | ✅ | |
| Balance hídrico FAO-56 | ✅ | |
| Reservorio, PCR, dotación, turnos (entrada manual) | ✅ | Integración con ANA / Junta |
| Cobertura hídrica y autonomía entre turnos | ✅ | |
| SPI (contexto, con ceros) | ○ | ✅ |
| SPEI | ❌ | ○ |
| IMERG | ○ si está listo | ✅ |
| SMAP v8 | ○ si está listo | ✅ |
| Economía SIEA/MIDAGRI (FAOSTAT respaldo) | ✅ (referencia) | ✅ |
| Ficha de preparación | ✅ | |
| Texto de alerta liviana | ○ | Envío real WhatsApp/SMS |
| F1 | ✅ | |
| F2 | ✅ | |
| F3 | ○ básico | ✅ |
| Vigilancia de antracnosis (POWER horario) | ❌ | ✅ |
| ECOSTRESS, S2, NDRE, GAEZ, ESAN, ML | ❌ | ✅ |

## **20.3. Orden de trabajo**

| Paso | Qué | Salida verificable |
| :---: | :---- | :---- |
| 1 | Descargar POWER 1981–2025 (`community=AG`) y verificar esquema, unidades y cobertura | Parquet con unidades validadas |
| 2 | ET0 FAO-56 con Ra, Rso, Rnl | Prueba Ejemplo 18 (±0,1 mm/día) |
| 3 | Catálogo (5 cultivos) en JSON con fuente y estado por parámetro | Esquema validado |
| 4 | GDD y noches frescas | Series por ventana |
| 5 | Escenarios P10/P50/P90 + años análogos (ICEN) | Tabla por ventana; hindcast básico |
| 6 | Balance FAO-56 + autonomía entre turnos | Cierre de masa ±0,1 mm |
| 7 | Entrada de reservorio, PCR, dotación y turnos; cobertura hídrica | Caso manual de §17.3 |
| 8 | F1 completa con las cuatro dimensiones | Flujo de punta a punta |
| 9 | F2 reutilizando el mismo motor (RT-01…RT-08) | Comparación de 5 cultivos |
| 10 | IMERG y SMAP solo si §19 los respalda; SPI con ceros como contexto | — |
| 11 | Casos extremos y resultados "por determinar" (RNF-05) | Pruebas |

**Pila mínima sugerida:** `requests`, `pandas`, `pyarrow`, `numpy` (módulo físico propio), `scipy.stats`, `shapely` + `pyproj` (EPSG:4326 → EPSG:32717), `pytest`; `FastAPI` si hay backend.

---

# **21. Riesgos**

| # | Riesgo | Mitigación |
| :---- | :---- | :---- |
| 1 | Presentar el documento como datos ya integrados | §19 explícita y estados de evidencia en pantalla |
| 2 | Tratar perennes como anuales | RT-01, RT-02 y advertencia de compromiso |
| 3 | Extrapolar 9 km de SMAP a una parcela | Advertencia de escala permanente |
| 4 | SMAP subestima en valle irrigado | Anclar el balance en riego declarado |
| 5 | IMERG falla en llovizna costera | Contraste con SENAMHI |
| 6 | SPEI mal calculado | Diferido; procedimiento de §10.2 y método de PET declarado si se retoma |
| 7 | Balance con unidades incompatibles o que resta ETc con suelo agotado | Convención única en mm y forma FAO-56 con ETc,adj (§9.3); prueba de cierre de masa |
| 8 | ENSO tratado como regla | §10.5 y condicionamiento con advertencias |
| 9 | Especie de limón equivocada | *Citrus × aurantiifolia* declarada y parámetros POR VALIDAR |
| 10 | GAEZ descarta cultivos sin contexto local | GAEZ como señal, no filtro |
| 11 | Reglas sin respaldo convertidas en automáticas | RT-04 degradada a advertencia |
| 12 | Índices presentados como evidencia independiente | §7.4 |
| 13 | Precio regional tomado como propio | Sobreescritura obligatoria |
| 14 | Alcance excesivo para 48 h | MVP de un solo flujo (§20) |
| 15 | Radiación POWER en unidad equivocada (factor 3,6) | `community=AG` + validación de unidad (EX-14) |
| 16 | Modelar la sequía como meteorológica en un valle regado | Prioridad hídrica invertida (§7.1); cobertura y autonomía (§9.4–9.5) |
| 17 | SPI inválido por meses de lluvia cero | Distribución mixta y regla q > 0,5 (§10.1) |
| 18 | Ignorar el efecto de El Niño en la floración del mango | Noches frescas (§9.6) |
| 19 | Presentar resultados de ML o un "score" como predicción | Sin ML ni índices agregados en el MVP (§2) |
| 20 | Dotación o PCR no disponibles a tiempo | Entrada manual y EX-15 |

---

# **22. Glosario**

| Término | Significado |
| :---- | :---- |
| Campaña | Periodo de manejo de un cultivo, de establecimiento a cosecha. |
| Rotación | Cambio planificado de cultivo entre campañas; aquí se evalúa como continuidad vs cambio para la próxima. |
| Perenne | Cultivo con vida productiva de varios años (mango, limón). |
| Periodo juvenil | Años antes de la primera producción. |
| ET0 / ETc | Evapotranspiración de referencia / demanda del cultivo. |
| GDD | Grados-día de desarrollo. |
| TAW / RAW / Dr | Agua disponible total / fácilmente disponible / agotamiento (mm). |
| SPI | Índice estandarizado de precipitación. |
| SPEI | Índice estandarizado de precipitación-evapotranspiración (balance acumulado + log-logística). |
| CDD | Días secos consecutivos. |
| ENFEN | Comisión peruana que declara el estado de El Niño / La Niña. |
| Escenario | Conjunto posible de condiciones futuras para comparar decisiones; no es predicción. |
| Hindcast | Prueba de un método contra el pasado para medir su acierto. |
| ETc,adj | Evapotranspiración real del cultivo ajustada por estrés hídrico (Ks·Kc·ET0). |
| PCR | Plan de Cultivo y Riego: área autorizada por cultivo y dotación de agua que fija la Junta de Usuarios para la campaña. |
| Dotación | Volumen de agua asignado por hectárea y campaña (m³/ha). |
| Cobertura hídrica (C) | Cociente entre agua asignada y demanda bruta del cultivo, ambos en m³. |
| Autonomía entre turnos | Días que el agua fácilmente disponible del suelo cubre la demanda del cultivo. |
| ICEN | Índice Costero El Niño (región Niño 1+2), publicado por ENFEN. |
| Inducción floral | Proceso que, tras un periodo fresco o de estrés, lleva al mango a florecer. |
| ECw | Conductividad eléctrica del agua de riego (salinidad del agua). |
| Diferido | Reconocido como necesario, fuera del MVP. |

---

# **23. Referencias**

- NASA Space Apps 2026 — reto y recursos — https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources
- NASA POWER — API diaria — https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- NASA GPM — IMERG — https://gpm.nasa.gov/data/imerg
- **NASA NSIDC — SMAP L4 v8** — https://nsidc.org/data/spl4smgp/versions/8
- FAO-56 — Allen et al., evapotranspiración del cultivo — https://www.fao.org/4/x0490e/x0490e0a.htm
- Vicente-Serrano et al. (2010) — SPEI — https://doi.org/10.1175/2009JCLI2909.1
- McKee et al. (1993) — SPI — https://doi.org/10.1175/1520-0442(1993)006<1103:TSOPIA>2.0.CO;2
- FAO GAEZ v4 — https://gaez.fao.org/
- FAOSTAT — https://www.fao.org/faostat/
- SENAMHI — https://www.senamhi.gob.pe/
- ENFEN — https://enfen.gob.pe/
- ANA — https://www.gob.pe/institucion/ana/
- MIDAGRI / SIEA — https://siea.midagri.gob.pe/
- INIA — laboratorios de suelos — https://app.inia.gob.pe/labsaf/publico/dashboard
- ISRIC SoilGrids — https://soilgrids.org/
- NASA AppEEARS — extracción de SMAP y ECOSTRESS por punto/polígono — https://appeears.earthdatacloud.nasa.gov/
- NASA GES DISC — https://disc.gsfc.nasa.gov/  ·  Giovanni — https://giovanni.gsfc.nasa.gov/
- NASA ECOSTRESS — https://ecostress.jpl.nasa.gov/
- Copernicus Data Space (Sentinel-2) — https://browser.dataspace.copernicus.eu/
- FAO-56, Ejemplo 18 (ET0 diaria) y ec. 85–88 (balance) — https://www.fao.org/4/x0490e/x0490e00.htm
- Ayers & Westcot (1985), FAO-29 — calidad del agua para agricultura (tolerancia a salinidad)
- ISO/IEC 25010:2023 — modelo de calidad del producto
- ISO/IEC/IEEE 29148:2018 — ingeniería de requisitos

---

# **Registro de cambios**

**v0.7** (a partir de la auditoría técnica de la v0.6)
1. Prioridad hídrica invertida: reservorio, PCR, dotación, turnos e ICEN pasan a Esenciales; SPI a contexto; SPEI diferido.
2. ET0 completa con Ra, Rso y Rnl; prueba contra el Ejemplo 18 de FAO-56.
3. Balance en forma FAO-56 (Dr) con ETc,adj; prueba de cierre de masa.
4. SPI con distribución mixta para ceros y regla q > 0,5.
5. POWER con `community=AG` y validación de unidades; resoluciones MERRA-2 / CERES declaradas.
6. Enum único de seis categorías de dato.
7. ENSO: ICEN como clasificador, serie 1981–2025, años análogos individuales cuando la muestra es pequeña; comunicados ENFEN en paralelo.
8. Nuevas derivadas: cobertura hídrica, autonomía entre turnos, noches frescas, percentil del reservorio (D-13 a D-17).
9. Nuevas variables V-30 a V-41; nueva regla RT-08 (área no autorizada en el PCR).
10. Tolerancia salina del caupí corregida (POR VERIFICAR con FAO-29).
11. Catálogo con decisión crítica por cultivo y variedad de mango.
12. ECOSTRESS y Sentinel-2 con papel definido para la fase posterior.
13. Decisiones explícitas: sin ML y sin "score de resiliencia" (ficha de preparación en su lugar).
14. Requisitos RF-17 dividido; RF-23 a RF-29; RNF-08 y RNF-09; criterios de aceptación ISO 29148; EX-14 a EX-18.
15. Referencias cruzadas de la cabecera corregidas.

**v0.6**
1. Horizonte único de una campaña; se elimina el cronograma multianual y se restauran F1/F2/F3.
2. Se agrega **frijol caupí** (y maíz opcional) para demostrar rotaciones convencionales.
3. Nueva §6: cómo se estiman las condiciones futuras y cómo se distinguen observado, pronosticado, escenario y simulado.
4. GPS reemplazado por **dibujo manual de parcela**.
5. **SMAP L4 v7 → v8**.
6. **SPEI** corregido: balance acumulado + log-logística de 3 parámetros.
7. **ESAN retirado** del MVP y marcado como diferido.
8. **Balance hídrico** revisado dimensionalmente, con convención única en mm.
9. **ENSO** reformulado como tendencia no determinista.
10. **Limón** corregido a *Citrus × aurantiifolia* con advertencia de parámetros.
11. **GAEZ** degradado de filtro a señal de aptitud.
12. **RT-04** degradada de regla automática a advertencia informativa.
13. Fuentes reorganizadas en **tres niveles de prioridad**.
14. Nueva §7.4 sobre **no independencia** de índices.
15. MVP reducido a **un flujo de extremo a extremo**.

**v0.5** — Dos tipos de decisión (D1/D2), catálogo arroz-mango-limón, GPS, historial, módulo de sequía.
**v0.4** — Contrato de 40 variables, capa física, IMERG, ECOSTRESS, NDRE, GAEZ, MIDAGRI, capa nacional.
**v0.3** — Horizonte de una campaña, seguimiento, motor compartido, cuatro dimensiones.
