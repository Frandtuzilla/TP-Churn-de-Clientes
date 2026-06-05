# decisions.md — Memoria del proyecto

> Registro de cada decisión importante. Regla: si pensarla te llevó más de 5 minutos, va acá.
> Lo consultás en la defensa oral. Formato por entrada: qué / por qué / alternativas descartadas / consecuencias.

---

## Decisión — Usar Claude Code en lugar de Cursor
1. **Qué decidí:** desarrollar el TP con Claude Code como editor/agente, en vez de Cursor.
2. **Por qué:** las skills que pide la cátedra (`grill-me`, `data-science-kit`, `gentle-ai`) son skills del ecosistema Claude y se instalan de forma nativa; el flujo Entender → Delegar → Validar y los subagentes (`ds-planner`, `ds-explorer`) funcionan igual o mejor.
3. **Alternativas que descarté:** Cursor (la opción por defecto de la consigna) — válida, pero no aporta ventaja para nuestro caso.
4. **Consecuencias:** mismo resultado de entrega; ligera diferencia en cómo se invocan las skills. A confirmar con el profe que acepta la herramienta.

---

## Decisión — Estructura del repositorio
1. **Qué decidí:** estructura estándar de proyecto de data science (`data/raw`, `notebooks`, `reports`, `src`) con el dataset original intocable en `data/raw/`.
2. **Por qué:** separa datos crudos de análisis y favorece reproducibilidad y commits limpios.
3. **Alternativas que descarté:** todo en un solo notebook (difícil de mantener y revisar).
4. **Consecuencias:** facilita que cada entrega sea un commit ordenado.

---

## Decisión — Foco de negocio y selección de 5 hipótesis (Semana 1)
1. **Qué decidí:** enfocar todo en **frenar el churn temprano** y elegir estas 5 hipótesis: el primer mes como campo de batalla (H1), la queja del cliente nuevo (H2, interacción), la satisfacción que no protege (H3, contraintuitiva), tier 2/3 + quejas (H4, interacción) y más dispositivos = más riesgo (H5, contraintuitiva).
2. **Por qué:** el objetivo del TP es la acción, no el dato. El primer mes concentra el 52% del churn, así que el lente "cliente nuevo" es donde la intervención llega a tiempo. Elegí dos interacciones (muestran *dónde/cuándo* actuar) y dos contraintuitivas (demuestran que validamos en vez de asumir, lo que más suma en la defensa).
3. **Alternativas que descarté:** soltero nuevo, categoría de entrada, método de pago, blindaje del primer año, app vs. computadora y distancia al depósito. Quedaron en `reports/00_hipotesis_candidatas.md` por si cambiamos alguna.
4. **Consecuencias:** un relato de negocio coherente y defendible; la validación estadística de cada hipótesis queda para Semana 2.

---

> ⏸️ **Las decisiones de abajo son de Semana 2/3 (modelado y reporte), adelantadas como prueba de concepto. Se revisan y confirman cuando corresponda — no son parte de la entrega de Semana 1.**

## Decisión — Unificar categorías inconsistentes
1. **Qué decidí:** mapear etiquetas duplicadas (`Phone`→`Mobile Phone`, `CC`→`Credit Card`, `Cash on Delivery`→`COD`, `Mobile`→`Mobile Phone`).
2. **Por qué:** son el mismo concepto escrito distinto; sin unificar, el modelo las trata como categorías separadas y se diluye la señal.
3. **Alternativas:** dejarlas como están (peor) o eliminarlas (perderíamos información).
4. **Consecuencias:** categóricas más limpias y un one-hot más compacto.

## Decisión — Split estratificado ANTES de imputar
1. **Qué decidí:** `train_test_split(test_size=0.2, stratify=y, random_state=42)` como primer paso, y toda imputación/escalado dentro de un pipeline ajustado solo con train.
2. **Por qué:** evita data leakage. Si imputo con la mediana de todo el dataset, el test "ve" información del train. Estratificar mantiene el 16,8% de churn en ambas partes.
3. **Alternativas:** split aleatorio simple (riesgo de desbalancear train/test) o imputar antes (contamina).
4. **Consecuencias:** train churn 16,8% / test 16,9%. Resultados reproducibles y honestos.

## Decisión — Tratamiento de nulos
1. **Qué decidí:** imputar numéricas con la **mediana** dentro del pipeline.
2. **Por qué:** ~4,5–5,5% de nulos en 7 columnas; la mediana es robusta a outliers (varias variables están sesgadas).
3. **Alternativas:** eliminar filas con nulos (perdería ~25% de los datos al acumularse) o imputar con la media (sensible a outliers).
4. **Consecuencias:** conservamos todas las filas sin distorsionar distribuciones.

## Decisión — Qué hacemos con Complain (leakage)
1. **Qué decidí:** mantener `Complain` en el modelo principal, pero documentar el riesgo y **medir su impacto** entrenando una versión sin ella.
2. **Por qué:** el diccionario dice "queja del último mes" → posible leakage temporal. La prueba mostró que sin `Complain` el recall solo baja de 86,3% a 81,1% (AUC 0,999→0,997): la variable ayuda pero no es imprescindible.
3. **Alternativas:** quitarla de una (innecesariamente conservador) o usarla sin chequear (riesgoso).
4. **Consecuencias:** conclusiones robustas; si el negocio confirma que la queja se registra después de la baja, la sacamos y casi no perdemos performance.

## Decisión — Métrica prioritaria: Recall (con F1 de control)
1. **Qué decidí:** optimizar y reportar sobre todo **recall**, acompañado de precision, F1 y AUC. **Accuracy queda descartada** como métrica de decisión.
2. **Por qué:** el costo de perder un cliente (5–25× el de retenerlo) supera el de una intervención innecesaria. Queremos no perdernos churners. Con 16,8% de churn, accuracy engaña (el baseline "no se va nadie" da 83,1%).
3. **Alternativas:** optimizar accuracy (inútil acá) o precision (dejaría escapar churners).
4. **Consecuencias:** preferimos algunas falsas alarmas a cambio de detectar más clientes en riesgo.

## Decisión — Modelo final: Random Forest
1. **Qué decidí:** **Random Forest** (300 árboles, `class_weight='balanced'`) como modelo final.
2. **Por qué:** mejor balance de métricas en test — recall 86,3%, precision 99,4%, F1 0,924, AUC 0,999 — superando ampliamente al baseline (recall 0%) y a Gradient Boosting (F1 0,742). El árbol simple tiene buen recall (83,7%) pero precision baja (43%).
3. **Alternativas:** árbol de decisión (más interpretable, lo usamos para explicar) y Gradient Boosting (peor recall acá).
4. **Consecuencias:** AUC casi perfecto → lo auditamos: lo explica Tenure (24% de importancia), no el leakage de Complain. Lo reportamos con honestidad.

---

> 📅 **Bloque de Semana 2 (EDA formal · 2026-06-05).** Decisiones tomadas
> durante la validación estadística de las 5 hipótesis. Cada una explica
> "qué decidí", "por qué", "alternativas descartadas" y "consecuencias",
> para que en la defensa se pueda contestar cada elección sin dudar.

## Decisión — Elegir Mann-Whitney / Chi-cuadrado / Fisher en vez de t-test / ANOVA
1. **Qué decidí:** usar tests **no paramétricos** (Mann-Whitney U, Chi-cuadrado, Fisher exacto, Spearman) en lugar de t-test/ANOVA para validar las 5 hipótesis y reportar tamaño de efecto (rank-biserial, Cramér's V, ρ, OR) además del p-valor.
2. **Por qué:** los tests KS rechazan normalidad en TODAS las variables numéricas (p < 10⁻⁶⁴ en `Tenure`, p ≈ 0 en `CashbackAmount`, etc.) y varias están fuertemente sesgadas. Aplicar t-test asumiendo normalidad sería metodológicamente débil; con n=5.630 hasta diferencias triviales darían p < 0,001, por eso reporto **siempre** el tamaño de efecto para distinguir "significativo" de "importante".
3. **Alternativas descartadas:** t-test de Welch (rechazado: supuesto de normalidad violado). Bootstrap (alternativa válida pero más opaca para la defensa). Reportar sólo p-valor (rechazado: con esta n cualquier cosa es significativa).
4. **Consecuencias:** las conclusiones son robustas al supuesto distribucional. Permite responder en la defensa "¿por qué no usaste un t-test?" con argumento técnico.

## Decisión — Reportar H4 como "parcialmente confirmada" y no inflarla
1. **Qué decidí:** declarar H4 como **parcialmente confirmada**. El efecto global tier×queja es contundente (p ≈ 10⁻⁸⁴), pero la comparación específica que la hipótesis afirma — "Tier 2/3 + queja peor que Tier 1 + queja" — sale **no significativa** (chi² focalizado p = 0,176). En `eda.md` y `hipotesis.md` se dice exactamente eso; el reporte ejecutivo no afirma la diferencia puntual.
2. **Por qué:** los datos visuales muestran 38,6% (tier 3+queja) vs 28,4% (tier 1+queja), pero con n=560 vs n=1.044 esa diferencia entra en el ruido. Vender la hipótesis como "totalmente confirmada" sería sostener algo que el test no respalda — el tipo de error que el evaluador busca.
3. **Alternativas descartadas:** (a) declararla confirmada apoyándonos sólo en el chi-cuadrado global (engañoso: el global captura el efecto de tier por un lado y queja por otro, no la interacción específica); (b) descartarla por completo (excesivo: sí hay efecto de tier y sí hay efecto de queja, y ambos importan para el modelo).
4. **Consecuencias:** **gana defensibilidad.** Si en la defensa preguntan "¿la queja pega más fuerte en el interior?", la respuesta honesta es: "el patrón visual lo sugiere, pero con esta muestra no podemos afirmarlo al α=0,05; sí podemos decir que tier 2/3 churnea más y que la queja triplica el churn en cualquier zona". Para el modelo, sigo conservando `CityTier` y `Complain` por separado.

## Decisión — Validar H3 (satisfacción) sólo en clientes nuevos
1. **Qué decidí:** validar la hipótesis "el score de satisfacción no protege" **restringiéndola a clientes nuevos** (`Tenure ≤ 1`), y reportar Spearman ρ además del χ² para mostrar la dirección del efecto.
2. **Por qué:** la hipótesis ORIGINAL hablaba de clientes nuevos (no del dataset completo). Mezclar a los establecidos diluye el efecto y oculta el hallazgo contraintuitivo. Spearman ρ = +0,14 en nuevos confirma que el score correlaciona POSITIVO con churn — un resultado fuerte para la defensa ("validamos en vez de asumir").
3. **Alternativas descartadas:** (a) validar sobre todo el dataset (diluye y vuelve la hipótesis trivial); (b) usar regresión logística con interacción `Tenure × SatisfactionScore` (más sofisticado pero menos legible para la cátedra; el χ² + Spearman cuenta lo mismo).
4. **Consecuencias:** el resultado contraintuitivo queda nítido (score 5 = 61,6% churn vs score 1 = 41,5% en nuevos). Para el negocio: dejar de usar el score como termómetro y revisar cómo/cuándo se mide.

## Decisión — Marcar Complain como leakage potencial y entrenar doble modelo
1. **Qué decidí:** mantener `Complain` en el modelo principal pero **entrenar y reportar también un modelo sin `Complain`** para medir el impacto. La hipótesis-test (¿es leakage?) la responde el delta de recall, no la intuición.
2. **Por qué:** el diccionario describe `Complain` como "queja del último mes" sin fecha exacta. Si la queja se registra al cancelar (no antes), la variable ve el futuro. Cramér's V = 0,25 con el target — alto, pero compatible con relación causal real (la queja también puede ser síntoma genuino previo a la baja). El único modo honesto de defenderlo es **medirlo**.
3. **Alternativas descartadas:** (a) eliminarla de una sin chequear el impacto (conservador pero ignorante); (b) dejarla sin advertir nada (riesgoso ante el evaluador); (c) inferir el timestamp con feature engineering (no se puede sin más datos).
4. **Consecuencias:** dos métricas en el reporte (con y sin), y una pregunta concreta para el área: "¿la queja se registra al recibirla, o al darse de baja?". La respuesta cambia la recomendación final.

## Decisión — Mantener variables sin señal en el modelo (no descartar por intuición)
1. **Qué decidí:** **conservar** en el dataset de modelado las variables que mostraron sin señal en el EDA (`HourSpendOnApp` p=0,23; `CouponUsed` p=0,27; `OrderAmountHikeFromlastYear` p=0,13). El árbol decide por feature importance.
2. **Por qué:** el EDA mira asociaciones marginales; el árbol detecta interacciones que el EDA no testeó (ej. `CouponUsed` puede importar dentro del subgrupo de Tier 3, aunque a nivel global no se vea). Descartar a mano introduce sesgo del analista.
3. **Alternativas descartadas:** (a) descartarlas para "simplificar el modelo" (premature optimization; mejor que la feature importance las elimine); (b) un feature selection automatizado tipo SelectKBest (innecesario con tan pocas features y un árbol que ya hace selección implícita).
4. **Consecuencias:** el handoff las marca como "prioridad baja, se espera bajo aporte". Si el árbol confirma la sospecha, se documenta y se discute en la defensa con datos, no con intuición.

## Decisión — Crear `EsNuevo` y `NuevoYQueja` como features explícitas (vs. dejar que el árbol las descubra)
1. **Qué decidí:** ingenierar dos features binarias derivadas: `EsNuevo = (Tenure ≤ 1)` y `NuevoYQueja = EsNuevo & Complain`, y agregarlas al pipeline del modelado.
2. **Por qué:** son operacionalizaciones directas de los dos hallazgos más fuertes del EDA (H1 y H2). El árbol las inventaría solo, pero explicitarlas (a) hace el modelo más legible para el reporte ejecutivo, (b) las hace visibles en SHAP (un nodo `NuevoYQueja=1` cuenta una historia clarísima), (c) protege al modelo más simple — si forzamos `max_depth=3`, una sola partición captura el segmento crítico.
3. **Alternativas descartadas:** (a) dejar que el árbol invente las cortes solo (válido pero genera nodos como `Tenure ≤ 0.5` que son menos legibles); (b) hacer un `KBinsDiscretizer` sobre `Tenure` (más general pero menos motivado por el negocio).
4. **Consecuencias:** el modelo final usa las dos banderas como inputs adicionales (no reemplazan `Tenure`/`Complain`). Para la defensa: dos features con nombre humano que se pueden señalar en el SHAP plot.

---

> 🛠️ **Bloque Feature Engineering (modo ML · 2026-06-05).** Decisiones tomadas
> durante la construcción del pipeline (`src/features/pipeline.py`) que
> produce `data/processed/features_{train,test}.parquet`. Cada una explica
> "qué decidí", "por qué", "alternativas descartadas" y "consecuencias",
> para defenderla en oral.

## Decisión — OneHotEncoder con `drop=None` (no `drop='first'`)
1. **Qué decidí:** OneHot **sin eliminar la primera categoría** en las 5 categóricas (`Gender`, `PreferredLoginDevice`, `PreferredPaymentMode`, `PreferedOrderCat`, `MaritalStatus`). Resultado: 17 dummies en lugar de 12.
2. **Por qué:** el modelo principal del TP es **árbol de decisión + Random Forest**. Para estos algoritmos, la multicolinealidad introducida por mantener todas las dummies (suma = 1 por grupo) es **inofensiva** — el árbol no resuelve sistemas lineales. Y mantener todas las categorías hace que cada una sea visible como split posible en el árbol y como contribución individual en SHAP — clave para el reporte y la defensa ("¿qué pasa con los clientes que pagan en COD?" → SHAP tiene esa columna identificable).
3. **Alternativas descartadas:** (a) `drop='first'` (-5 columnas; obligatorio si quisiera correr regresión logística sin regularización, pero hace que la categoría "base" desaparezca del SHAP); (b) TargetEncoder (innecesario: cardinalidad máxima = 5; TargetEncoder introduce riesgo de leakage si se fitea mal y sólo paga si cardinalidad > 15).
4. **Consecuencias:** dataset más ancho (33 features vs 28) pero **más legible para la defensa**. Si después se decide probar LogReg, hay que recomponer el pipeline cambiando a `drop='first'` — el `build_pipeline()` hace fácil esa variante.

## Decisión — Crear flag de missingness sólo para `Tenure`, no para las 7 columnas con nulos
1. **Qué decidí:** agregar **una sola** flag binaria `Tenure_was_na` (1 si el valor original era NaN). Para las otras 6 columnas con nulos (`WarehouseToHome`, `HourSpendOnApp`, etc.), imputar mediana sin flag.
2. **Por qué:** `Tenure` es el **predictor #1** del dataset (rank-biserial -0,63). Si el null es informativo ("clientes recién registrados que ni siquiera tienen tenure cargado"), perder esa señal cuesta caro. Para las otras variables, los nulos son ~4,5% repartidos uniformemente, sin patrón obvio que justifique +6 columnas de ruido potencial.
3. **Alternativas descartadas:** (a) ninguna flag (asume null aleatorio; defendible pero más débil); (b) flag para las 7 (+6 columnas, mayoría son ruido — el ROI de cada flag adicional es decreciente y agrega correlaciones espurias).
4. **Consecuencias:** dataset gana 1 columna interpretable. Si el árbol no la usa (feature importance ≈ 0), el Modeler puede dropearla con justificación; si la usa, es defensible como "missingness informativa en el predictor #1".

## Decisión — Umbral `Tenure ≤ 3` para `tenure_bajo_queja` (no `Tenure ≤ 1` como en el EDA)
1. **Qué decidí:** usar **`Tenure ≤ 3 meses`** (no ≤ 1) en la feature derivada `tenure_bajo_queja`. La hipótesis H2 del EDA usaba la definición estricta `EsNuevo = Tenure ≤ 1`; acá ampliamos el ventana a "primer trimestre".
2. **Por qué:** el umbral lo fijó el usuario en el prompt original. Es **operativamente más útil** que el ≤ 1: en el EDA, los buckets 0-1m y 2-3m juntos concentran la mayoría del riesgo del primer cuarto de año (51,8% + 8,8% de churn), y el equipo de retención tiene más margen de maniobra con una ventana de 3 meses que de 1. Verificación post-pipeline: dentro de la flag = 1 el churn es 66,0% (vs 73% que reportó H2 con el umbral más estricto). Sigue siendo un segmento de altísima señal.
3. **Alternativas descartadas:** (a) `Tenure ≤ 1` (más afilado pero captura menos clientes — 5,6% del train vs 9,2% — y es menos accionable para retención); (b) `Tenure ≤ 6` (demasiado ancho — la tasa de churn dentro cae a ~35% y diluye la señal).
4. **Consecuencias:** la feature señala un segmento operativamente relevante (9,2% del padrón con 66% de churn esperado). Si el árbol decide no usarla, queda como información para el reporte ejecutivo ("estos 410 clientes del train son los del primer trimestre con queja").

## Decisión — `RobustScaler` para TODAS las numéricas (no `StandardScaler`)
1. **Qué decidí:** aplicar `RobustScaler` (centra en la mediana, escala por IQR) a las **12 variables numéricas** del pipeline — tanto las 9 continuas como las 3 ordinales (`CityTier`, `SatisfactionScore`, `NumberOfDeviceRegistered`).
2. **Por qué:** el EDA mostró que varias features tienen **outliers o colas largas** sin que sean errores de carga: `WarehouseToHome` (max 127 km con p99=40), `OrderCount` (skew 2,2, 12,5% outliers IQR), `CouponUsed` (skew 2,5, 11% outliers), `CashbackAmount` (skew 1,1). `StandardScaler` usa media/desvío y se contamina con esas colas (la media se desplaza hacia los outliers, el desvío se infla). `RobustScaler` usa mediana e IQR, que son invariantes a los extremos.
3. **Alternativas descartadas:** (a) `StandardScaler` (más clásico pero rompe la escala si hay outliers — y los hay); (b) `log1p + StandardScaler` (mejor para asimetrías muy fuertes, pero agrega complejidad y rompe la interpretabilidad — un `Tenure` log-transformado es menos legible en SHAP); (c) Sin escalar (válido para árboles, pero si después se prueba LogReg el modelo se contamina con la escala absoluta de cashback vs tenure).
4. **Consecuencias:** distribuciones centradas en 0 (mediana exacta = 0 en train, verificado), resistentes a outliers, agnósticas al algoritmo final. Si el Modeler quiere LogReg también, el dataset ya está escalado. Para árbol/RF: irrelevante pero no daña.
