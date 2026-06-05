# EDA — E Commerce Churn

**Fecha:** 2026-06-05
**Dataset:** `data/raw/E_Commerce_Dataset.xlsx` (hoja `E Comm`) · 5.630 clientes
**Target:** `Churn` (1 = el cliente se fue, 0 = se quedó). Tasa global: **16,84%**
**Notebook ejecutable:** `notebooks/01_eda.ipynb`

Este documento concentra los hallazgos accionables del análisis exploratorio.
La validación formal de las 5 hipótesis vive en [`hipotesis.md`](./hipotesis.md);
los problemas de datos en [`data_quality.md`](./data_quality.md); el resumen
para el siguiente paso en [`handoff_to_modeler.md`](./handoff_to_modeler.md).

---

## 1. La pregunta de negocio que guía todo

> Detectar a los clientes con alto riesgo de churn **antes** de que se vayan
> para que el equipo de retención pueda intervenir a tiempo. Y entender **por
> qué** se van: qué palanca activar y sobre quién.

Esa pregunta marca el rumbo del EDA: priorizamos variables y subgrupos donde
una **intervención del negocio** es posible (onboarding, atención de quejas,
cashback dirigido, segmentación geográfica), no solo lo que da p-valor bonito.

---

## 2. Foto del dataset

- **Tamaño:** 5.630 filas, 20 columnas (1 ID + 1 target + 18 features).
- **Balance del target:** 4.682 (83,16%) no-churn vs 948 (16,84%) churn.
  Desbalance moderado, ~1:5. Suficientemente fuerte como para descartar
  *accuracy* y priorizar **recall** y **PR-AUC** ([gráfico](figures/eda_01_target_balance.png)).
- **Nulos:** 7 columnas con 4,5–5,5% de nulos cada una (todas numéricas
  continuas). Todo el resto está completo. Se imputa post-split, mediana.
- **Duplicados:** 557 pares idénticos con `CustomerID` distinto. Esperable
  por la baja cardinalidad de varias variables; no son error de carga
  (detalle en `data_quality.md`).

---

## 3. ¿Qué predice el churn? — variables con señal real

Top 5 features numéricas por correlación absoluta con `Churn` (point-biserial,
todas con p < 0,001):

| Variable | |r| | Lectura |
|---|---:|---|
| `Tenure` | 0,349 | **El predictor #1 del dataset.** Mediana 9 m. Cae en escalón después del primer mes. |
| `Complain` | 0,250 | Bandera de queja. Riesgo de leakage temporal — ver §7. |
| `DaySinceLastOrder` | 0,161 | Más días sin comprar = mayor probabilidad de churn (curioso: signo negativo en `pointbiserial`, ver nota). |
| `CashbackAmount` | 0,154 | Más cashback = menos churn. Asociación monotónica (ver §5). |
| `NumberOfDeviceRegistered` | 0,108 | **Asociación POSITIVA con churn** — más dispositivos, más fuga. Contraintuitivo (H5). |

> Nota sobre el signo de `DaySinceLastOrder`: con la definición de "días desde
> el último pedido", uno esperaría más días → más churn. Acá la correlación
> sale **negativa**: los que se quedan tienen más promedio de "días sin
> comprar". Es probable que el campo no represente lo que el nombre sugiere
> (¿días promedio entre pedidos? ¿días al último pedido medidos solo entre
> compradores activos?). **Recomendación: pedirle al área que confirme la
> definición antes de modelar**; mientras tanto, dejarla en el modelo pero
> evitar interpretarla en el reporte ejecutivo.

Top 3 features categóricas por Cramér's V (asociación con `Churn`):

| Variable | V | Categoría más churneadora | Tasa |
|---|---:|---|---:|
| `PreferedOrderCat` | 0,226 | `Mobile Phone` | 27,4% |
| `MaritalStatus` | 0,183 | `Single` | 26,7% |
| `PreferredPaymentMode` | 0,096 | `COD` | 24,9% |

Otras variables que **no muestran señal** (después de probar 2+ encodings):
`HourSpendOnApp` (p=0,23 Mann-Whitney), `CouponUsed` (p=0,27),
`OrderAmountHikeFromlastYear` (p=0,13). Documentado para que el Modeler las
incluya pero no espere mucho de ellas — el árbol decidirá si las usa.

---

## 4. Las 5 hipótesis — veredicto (detalle estadístico en `hipotesis.md`)

| Hip. | Enunciado | Resultado | Acción que habilita |
|---|---|---|---|
| **H1** | Tenure bajo → más churn | ✅ Confirmada con efecto **grande** (rank-biserial = -0,63) | Programa de onboarding en los primeros 30 días |
| **H2** | Nuevo + queja → churn desproporcionado | ✅ Confirmada (OR = **21,7**; 73% vs 4% en el extremo opuesto) | Atención prioritaria a quejas de clientes con <30 días |
| **H3** | Satisfacción alta NO protege a los nuevos | ✅ Confirmada y contraintuitiva (Spearman **+0,14**: score alto correlaciona con MÁS churn en nuevos) | Dejar de usar el score como termómetro; basar alertas en comportamiento |
| **H4** | Tier 2/3 + queja peor que Tier 1 + queja | ⚠️ **Parcialmente.** El efecto global tier×queja existe (p<10⁻⁸³), pero la comparación directa **no es estadísticamente significativa** (p=0,176) | Reforzar logística tier 2/3 igual; *no* publicar el delta específico sin más datos |
| **H5** | Más dispositivos = más churn | ✅ Confirmada y contraintuitiva (1 dispositivo 9,4% vs 6 dispositivos 34,6%) | Investigar señales de multicuenta / "shopping around" |

> 📌 **Honestidad del análisis.** H4 es el caso donde más se ve la diferencia
> entre "lo que esperábamos" y "lo que dicen los datos": el patrón visual
> existe (tier3+queja 38,55%, tier1+queja 28,35%) pero con n=560 contra
> n=1.044, la diferencia entra dentro del ruido. Lo decimos como tal en el
> reporte ejecutivo; no inflamos. Para una conclusión firme habría que sumar
> más datos o achicar la pregunta (p. ej. comparar dentro de un mismo
> MaritalStatus o tenure-bucket).

---

## 5. Hallazgos adicionales pedidos por negocio

### ¿En qué momento del tenure se concentra el churn?
[**Gráfico**](figures/extra_tenure_concentration.png)

- **El 71,6% de TODOS los churners se va en el primer mes.**
- Al mes 6, ya se fue el 80,4% de los churners totales.
- Después del mes 24, la tasa cae a 0% en los datos.
- Implicación: la ventana de intervención es muy corta. Cualquier modelo que
  no esté disponible en los primeros 30 días llega tarde.

### ¿Qué combinación de variables tiene mayor riesgo?
[**Gráfico**](figures/extra_top_risk_segments.png)

Top 4 segmentos por tasa de churn (CityTier × Complain × EsNuevo):

| Segmento | n | Tasa de churn |
|---|---:|---:|
| Tier 1 · **Con queja · Nuevo** | 274 | **72,6%** |
| Tier 3 · **Con queja · Nuevo** | 156 | **70,5%** |
| Tier 2 · Sin queja · Nuevo | 30 | 66,7% (muestra chica — interpretar con cautela) |
| Tier 3 · Sin queja · Nuevo | 252 | 47,6% |

**Lectura clave:** el predictor dominante NO es la zona, es la combinación
"nuevo + queja". El Tier 1 con queja y nuevo está prácticamente empatado con
Tier 3. Esto reordena prioridades: invertir en respuesta a quejas tempranas
rinde igual en cualquier tier; reforzar logística en tier 2/3 es una segunda
palanca (más cara, mayor capilaridad).

### ¿El cashback retiene?
[**Gráfico**](figures/extra_cashback.png)

| Quintil de cashback | Tasa de churn |
|---|---:|
| Q1 (`$0 – $140`) | **26,6%** |
| Q2 (`$141 – $154`) | 22,4% |
| Q3 (`$154 – $173`) | 12,6% |
| Q4 (`$173 – $209`) | 13,7% |
| Q5 (`$209 – $325`) | **8,9%** |

- Spearman r = -0,17 (p ≈ 0). Asociación monotónica clara.
- Promedio cashback no-churn = $180,6 · churn = $160,4.
- **Asociación, no causalidad.** Los clientes que reciben más cashback
  podrían ser ya clientes más comprometidos (los premium quizás). Para
  afirmar que "subir cashback retiene", haría falta un experimento A/B.
  Para el modelo, es una variable predictiva sólida; para el reporte, hay
  que matizarlo.

---

## 6. Distribuciones y comparativas — qué hay que mirar

- **Tenure:** sesgo positivo (skew 0,74), mediana 9 meses. La distribución de
  los churners está concentrada en el extremo izquierdo (≤1 mes); la de los
  no-churners es bimodal con masa entre 7 y 25 meses.
- **CashbackAmount:** sesgo derecho (skew 1,15), cola hasta $325. Los churners
  se ubican en la mitad inferior.
- **NumberOfDeviceRegistered:** distribución discreta 1-6, concentrada en 3-4.
  Los grupos 5 y 6 son los más churneadores (22,5% y 34,6%).
- **CityTier:** mayoría en Tier 1 (~65%), pero Tier 3 tiene tasa de churn
  más alta (21,4% vs 14,5% Tier 1).
- **SatisfactionScore:** distribución relativamente uniforme entre 1 y 5.
  Asociación con churn **positiva** (no esperada) — ver H3.

---

## 7. Variables sospechosas de leakage

**Únicamente `Complain`.** Detalles en `data_quality.md` §6 y en el handoff.

- Razón: el diccionario dice "queja del último mes" sin fecha exacta. Si la
  queja se registra al cancelar (no antes de cancelar), `Complain` ve el
  futuro.
- Mitigación: entrenar el modelo principal con `Complain`, comparar contra
  modelo sin ella, y reportar ambas métricas. Pedirle confirmación al
  negocio sobre cuándo se captura la queja.

**No detectadas** otras formas de leakage:
- Ninguna feature tiene |r| > 0,5 con el target (el más alto es `Tenure` con
  0,35, esperable).
- Ningún campo binario coincide >95% con `Churn` (test de duplicado de
  target). `Complain` está lejos de ser una réplica del target.

---

## 8. Implicaciones para el modelado (resumen)

(El handoff completo está en [`handoff_to_modeler.md`](./handoff_to_modeler.md).)

1. **Métrica:** priorizar **Recall** y **PR-AUC** sobre accuracy. Costo de
   perder un cliente ≫ costo de un falso positivo.
2. **Split:** `train_test_split(stratify=y, test_size=0.2, random_state=42)`.
   Imputación dentro del pipeline, ajustada solo con train.
3. **Modelo baseline obligatorio:** `DummyClassifier(strategy="most_frequent")`
   o "predecir siempre 0". Va a dar accuracy ≈ 83% y recall 0%. Ese es el piso.
4. **Modelo principal sugerido:** árbol de decisión (interpretable, exigido
   por la cátedra) + comparación con Random Forest. Probar
   `class_weight='balanced'`.
5. **Variable `EsNuevo = (Tenure ≤ 1)`:** crear como feature explícita para
   que el árbol no tenga que inventarla.
6. **`Complain`:** dos versiones del modelo (con y sin).
7. **Features sin señal a deprior­izar:** `HourSpendOnApp`, `CouponUsed`,
   `OrderAmountHikeFromlastYear`.
