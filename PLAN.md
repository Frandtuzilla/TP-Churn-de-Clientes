# Plan de Trabajo — TP Churn de Clientes

**Materia:** Inteligencia Artificial Aplicada a Negocios · Lic. en Negocios y Tecnología
**Tu rol:** Analista de retención / responsable de negocio (NO programador).
**Pregunta central:** ¿Podemos detectar qué clientes están por irse *antes* de que dejen de comprar? ¿Por qué nos dejan?
**Regla de oro de la cátedra:** No gana el modelo más preciso. Gana el que entiende qué resuelve, por qué funciona, qué límites tiene y sabe explicárselo a un gerente. *"Si no podés explicar por qué la IA hizo lo que hizo, no estás listo para la defensa."*

> **📍 Estado actual: Semana 1.** El trabajo activo es setup + entender el negocio + *formular* hipótesis. Entregables de S1: `reports/00_entendimiento_negocio.md` (las 3 preguntas), `reports/01_hipotesis.md` (las 5 elegidas), `notebooks/00_semana1.ipynb` (df.head + 1 gráfico por hipótesis) y el repo subido a GitHub.
> Nota: el **modelado, las métricas/SHAP y el reporte ejecutivo** (Fases 3–4) ya están **adelantados** como prueba de concepto, pero corresponden a **Semanas 2 y 3** — se retoman y validan cuando toque, no son parte de la entrega de S1.

---

## 1. Qué se evalúa (y cuánto pesa)

| Dimensión | Peso | Qué tenés que demostrar |
|---|---|---|
| Entendimiento del problema y los datos | Alto | Sabés qué pregunta respondés y con qué datos |
| Análisis exploratorio e hipótesis de negocio | Alto | Tus hipótesis tienen lógica de negocio y las validaste |
| Modelado, métricas y elección justificada | Medio | Elegiste bien la métrica y sabés por qué ese modelo |
| Comunicación ejecutiva y defensa oral | Alto | Se lo explicás a un gerente y defendés cada decisión |

**Traducción:** el código es un medio. Lo que se califica es tu criterio de negocio y tu capacidad de defenderlo.

---

## 2. Herramientas

- **Claude Code** (en lugar de Cursor): mismo flujo que pide la consigna, pero las skills viven de forma nativa.
  - `grill-me` → te interroga sobre un concepto hasta que lo entendés (clave para la defensa).
  - `data-science-kit` → subagentes `ds-planner` (plan en fases) y `ds-explorer` (perfilado de datos).
  - `gentle-ai` → memoria (Engram), "gentleman voice" (tutor en criollo) y `sdd-flow` para orquestar subagentes.
- **Python**: pandas, numpy, scikit-learn, matplotlib/seaborn, scipy (tests estadísticos), shap (interpretabilidad), openpyxl, jupyter.
- **GitHub**: repo con commits frecuentes. Cada hito = un commit.
- **decisions.md**: tu memoria del proyecto. Cada decisión que te costó >5 min pensar, va acá.

---

## 3. Calendario real (consigna v2)

Hoy es **viernes 05/06**. Fechas de entrega actualizadas según la consigna nueva:

| Entrega | Qué incluye | Fecha | Días desde hoy |
|---|---|---|---|
| EDA + Código/GitHub/Skills + decisions.md (parcial) | Repo base, entorno, skills, EDA con hipótesis y gráficos | **12/06** | 7 días |
| Notebook Modelado + decisions.md (final) + Reporte ejecutivo + Defensa oral | Baseline + árbol (obligatorio) con métricas correctas, PDF 4–6 pág. y presentación de 15 min | **19/06** | 14 días |

> ✅ **La contradicción de fechas quedó resuelta** en esta versión: el EDA ahora es claramente el **12/06** (alineado con "Semana 2"). Ya no hace falta consultarlo con el profe.
> ⚠️ **Ojo:** la entrega final del **19/06** ahora concentra modelado + reporte + defensa. Conviene tener el modelado listo unos días antes para preparar bien la defensa.

---

## 4. Las fases

### Fase 1 — Setup y entendimiento del problema  → para el 12/06  *(✅ hecho y subido a GitHub)*
**Objetivo:** entorno funcionando y entender el negocio antes de tocar datos.

- [ ] Repo en GitHub con la estructura del proyecto (ya armada en esta carpeta).
- [ ] Entorno Python con dependencias (`requirements.txt`).
- [ ] Instalar skills (`grill-me`, `data-science-kit`, `gentle-ai`).
- [ ] Copia del dataset en `data/raw/` — **NUNCA editar ahí**. ✅ hecho.
- [ ] Responder por escrito (va al reporte y a la defensa):
  - ¿Qué es churn y por qué le importa económicamente a la empresa?
  - ¿Qué significa que adquirir un cliente nuevo cuesta 5–7× más que retener uno? (en e-commerce, 5–25×)
  - ¿Qué decisión concreta toma el gerente comercial con tu análisis? (a quién intervenir, con qué presupuesto, cuándo)
- [ ] **Checkpoint obligatorio:** cargar el dataset y que `df.head()` funcione. Primer commit hecho.

### Fase 2 — EDA + hipótesis de negocio  → 12/06  *(Semana 2)*
**Objetivo:** entender quiénes son los clientes y qué patrones predicen churn. Todo con gráficos y tablas, **sin modelar todavía**.

- [ ] Perfilado completo: stats básicas, % de nulos por columna, tipos, cardinalidad de categóricas.
- [ ] Distribuciones (histogramas/boxplots) y detección de outliers.
- [ ] Correlaciones entre variables numéricas.
- [ ] Segmentación **churn vs. no-churn**: ¿en qué se diferencian?
- [ ] **5 hipótesis de negocio** en `reports/01_hipotesis.md`, cada una con: gráfico + test estadístico + interpretación en lenguaje de negocio. (Plantilla ya cargada con H1–H5.)
- [ ] **Análisis de leakage**: revisar variables sospechosas (sobre todo `Complain`, que el diccionario marca como "último mes"). Documentar el riesgo.
- [ ] **Split estratificado** train/test (`stratify=y`, `test_size=0.2`, `random_state=42`) — **PRIMERO**, antes de imputar/escalar nada, para no "espiar el examen".

### Fase 3 — Modelado y métricas  → 19/06  *(Semana 3 — requisitos actualizados en consigna v2)*
**Objetivo:** demostrar que la herramienta funciona y que elegiste la métrica correcta.

- [ ] **Manejo de nulos**: imputación dentro de un pipeline, ajustada solo con train (post-split).
- [ ] **Modelo baseline**: el más simple posible (predecir "no se va nadie" / DummyClassifier). Tu piso de comparación.
- [ ] **Árbol de decisión — OBLIGATORIO** (fácil de explicarle al gerente). **Random Forest — opcional** (más robusto; pedirle atención extra a la clase minoritaria).
- [ ] **Validación cruzada `StratifiedKFold` k=5** (repetir 5 veces manteniendo el 17/83) para que el resultado no sea suerte.
- [ ] **Métricas correctas** (NO accuracy): **Recall** (la más importante para el negocio), **Precision**, **PR-AUC**. Más matriz de confusión.
- [ ] **Desbalance** (~17%): `class_weight` / atención a la clase minoritaria — justificar la elección.
- [ ] **Interpretabilidad**: feature importance (ojo, no es causal) + **SHAP global y local**.
- [ ] `decisions.md` al día con cada decisión y sus alternativas descartadas.

> 🔁 **Ajuste vs. lo ya adelantado:** nuestro `02_modelado.ipynb` usa split simple + F1/ROC-AUC + Random Forest como estrella. Para la consigna v2 hay que **centrarlo en el árbol de decisión**, agregar **StratifiedKFold k=5** y reportar **PR-AUC**. Se adapta cuando lleguemos a S3.

### Fase 4 — Comunicación y defensa  → 19/06  *(Semana 3 — adelantado, parado)*
**Objetivo:** traducir todo a decisiones de negocio y defenderlo.

- [ ] **Reporte ejecutivo (PDF 4–6 pág.)** sin tecnicismos. Estructura sugerida:
  1. El problema en plata (cuánto cuesta el churn).
  2. Qué encontramos (3–4 hallazgos clave con gráficos simples).
  3. Qué hace el modelo y qué tan confiable es (en lenguaje de negocio).
  4. Quiénes son los clientes en riesgo y por qué.
  5. Recomendaciones de retención accionables (a quién, cómo, cuándo).
  6. Límites y próximos pasos.
- [ ] **Defensa oral (15 min)**: guion + anticipar las preguntas filosas (ver §6).
- [ ] Repasar el **glosario** con `grill-me` hasta poder explicar cada término sin leer.

---

## 5. decisions.md — qué vamos a registrar

Decisiones clave que sí o sí documentamos (con qué, por qué, alternativas, consecuencias):

- Elección de herramienta (Claude Code) — *ya registrada*.
- Cómo tratamos los nulos y por qué.
- Qué hacemos con `Complain` (¿la usamos o la sacamos por leakage?).
- Tipo de split y por qué estratificado.
- Métrica prioritaria elegida (recall/precision/PR-AUC) y su justificación de negocio.
- Modelo final elegido y por qué le ganó al baseline.
- Umbral de decisión (si lo movemos del 0.5 por defecto).

---

## 6. Riesgos y cosas a cuidar (las preguntas que te van a hacer)

- **Accuracy engañosa**: decir "no se va nadie" da ~83% y es inútil. Por eso miramos recall/precision/PR-AUC.
- **Data leakage**: ¿`Complain` se registró antes o después de irse? Si fue después, usarla es hacer trampa.
- **Imputar/escalar antes del split**: contamina el test. Siempre split primero.
- **Split no estratificado**: con 17% de churn, el azar puede desbalancear train vs. test.
- **Confundir correlación con causa**: una hipótesis validada estadísticamente describe asociación, no necesariamente causa.
- **Modelo que no le gana al baseline**: si pasa, algo está mal — es señal, no fracaso.

---

## 7. Estructura del repo

```
tp-churn-ecommerce/
├── PLAN.md                       ← este archivo
├── README.md
├── decisions.md                  ← memoria de decisiones
├── prompts_claude_code.md        ← prompts S1 (1º: subir Fase 1 a GitHub)
├── requirements.txt
├── .gitignore
├── data/
│   └── raw/E_Commerce_Dataset.xlsx    ← original, NO editar
├── notebooks/
│   ├── 00_semana1.ipynb          ← S1: df.head + gráfico por hipótesis  ✅
│   ├── 01_eda.ipynb              ← S2 (adelantado)
│   └── 02_modelado.ipynb        ← S3 (adelantado)
├── reports/
│   ├── 00_entendimiento_negocio.md   ← S1: las 3 preguntas  ✅
│   ├── 00_hipotesis_candidatas.md    ← menú para elegir
│   ├── 01_hipotesis.md               ← S1: las 5 elegidas  ✅
│   ├── 02_guion_defensa.md           ← S3 (adelantado)
│   ├── figures/                      ← gráficos
│   └── reporte_ejecutivo.pdf         ← S3 (adelantado)
└── src/                          ← funciones reutilizables (data_prep.py)
```

---

## 8. Próximo paso (cierre de Semana 1)

1. Revisar/ajustar las **5 hipótesis** (`reports/01_hipotesis.md`) y las **3 respuestas de negocio** (`reports/00_entendimiento_negocio.md`).
2. Correr el **PROMPT 1** de `prompts_claude_code.md` para **subir toda la Fase 1 a GitHub** (con el checkpoint: df.head + primer commit).
3. Repasar los conceptos con **`grill-me`** antes de dar la semana por cerrada.

Recién en **Semana 2** se valida cada hipótesis con test estadístico y se prepara el split. El modelado/reporte ya adelantados se retoman ahí.
