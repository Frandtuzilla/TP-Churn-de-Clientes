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

