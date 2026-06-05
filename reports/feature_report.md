# Feature Engineering Report

**Fecha:** 2026-06-05
**Modo:** ML
**Input:** `data/raw/E_Commerce_Dataset.xlsx` (hoja `E Comm`) · 5.630 filas × 20 columnas
**Output:** `data/processed/features_train.parquet`, `data/processed/features_test.parquet`
**Pipeline reproducible:** `src/features/pipeline.py` — función `build_pipeline()` (sin fitear) y `run_pipeline()` (orquestación completa).
**Split:** 4.504 train (80%) / 1.126 test (20%) · `stratify=y` · `random_state=42`
**Churn rate post-split:** train 16,83% · test 16,87% (estratificación correcta).
**Shape final:** train (4.504 × 34) · test (1.126 × 34) — 32 features + `Churn` + (índice implícito).

---

## 1 · Orden de ejecución (estricto)

1. Cargar raw (`data/raw/E_Commerce_Dataset.xlsx`).
2. **Corregir inconsistencias de etiquetas** (no aprende nada del dato — se aplica antes del split).
3. Separar `X` / `y`. **Drop `CustomerID`** (no es feature predictiva).
4. **Split estratificado** `test_size=0.2, stratify=y, random_state=42`. **Antes de cualquier `fit`.**
5. `fit` del `ColumnTransformer` con TRAIN. Aplicar `transform` a TRAIN y TEST.
6. Agregar **flag `Tenure_was_na`** (basada en el raw pre-imputación).
7. Agregar **features derivadas** `tenure_bajo_queja` y `citytier_alto_queja` (usando `Tenure`/`CityTier`/`Complain` en escala original post-imputación).

> **Regla dura:** `SimpleImputer` y `RobustScaler` se fitean **solo con train**. El test entra como invitado: solo `transform`. Esto se verifica con el sanity check de medianas en train (todas exactamente 0).

---

## 2 · Inconsistencias corregidas (pre-split)

| Columna | Mapping aplicado | Razón |
|---|---|---|
| `PreferredLoginDevice` | `Phone` → `Mobile Phone` | Misma categoría con dos etiquetas |
| `PreferredPaymentMode` | `CC` → `Credit Card`; `Cash on Delivery` → `COD` | Idem |
| `PreferedOrderCat` | `Mobile` → `Mobile Phone` | Idem (la columna mantiene el typo del original) |

No aprende nada del dato; aplicarlo antes del split es seguro y necesario para que train y test compartan vocabulario.

---

## 3 · Columnas dropeadas

| Columna | Razón |
|---|---|
| `CustomerID` | Identificador; sin valor predictivo. |

**No se dropea `Complain` aquí.** El handoff del Explorer pide entrenar dos modelos (con/sin `Complain`); el dropeo va al Modeler para evitar duplicar artefactos. La columna queda intacta en el parquet.

---

## 4 · Transformaciones por variable

### Numéricas continuas — imputación (mediana) + RobustScaler

| Variable | Nulos (raw) | Imputación | Escalado | Justificación |
|---|---:|---|---|---|
| `Tenure` | 4,69% | mediana | RobustScaler | Skew 0,74 + variable más predictiva (rank-bis -0,63). RobustScaler usa IQR — no se rompe con la cola de >24 meses. |
| `WarehouseToHome` | 4,46% | mediana | RobustScaler | Skew 1,62; cola larga con `max=127` km — RobustScaler la absorbe sin distorsionar la masa central. |
| `HourSpendOnApp` | 4,53% | mediana | RobustScaler | Sin señal en EDA (Mann-Whitney p=0,23) pero la dejamos; el árbol decide. |
| `NumberOfAddress` | 0% | (no aplica) | RobustScaler | Skew 1,09. Sin nulls; sólo se escala. |
| `OrderAmountHikeFromlastYear` | 4,71% | mediana | RobustScaler | Sin señal en EDA (p=0,13). |
| `CouponUsed` | 4,55% | mediana | RobustScaler | Skew 2,55; sin señal en EDA (p=0,27). Cola larga (max 16) — RobustScaler tolera. |
| `OrderCount` | 4,58% | mediana | RobustScaler | Skew 2,20; señal débil (p=0,036). Cola larga. |
| `DaySinceLastOrder` | 5,45% | mediana | RobustScaler | Señal media (Mann-Whitney p≈10⁻⁴²) pero **signo contraintuitivo** — ver warning §8. |
| `CashbackAmount` | 0% | (no aplica) | RobustScaler | Skew 1,15; señal media (p≈10⁻³⁸). |

### Numéricas ordinales — sólo escalado (sin imputación, sin nulls)

| Variable | Rango original | Escalado | Justificación |
|---|---|---|---|
| `CityTier` | {1, 2, 3} | RobustScaler | Ordinal con orden natural. Para árboles no afecta; para LogReg ayuda. |
| `SatisfactionScore` | {1..5} | RobustScaler | Idem. Caveat: en clientes nuevos correlaciona POSITIVO con churn (ver H3 del EDA). |
| `NumberOfDeviceRegistered` | {1..6} | RobustScaler | Idem. Patrón monotónico confirmado en H5. |

### Categóricas — OneHotEncoder (`drop=None`, `handle_unknown='ignore'`)

| Variable | Cardinalidad | Dummies generadas | Justificación |
|---|---:|---:|---|
| `PreferredLoginDevice` | 2 | 2 | Cardinalidad baja sin orden. `drop=None` para que cada categoría sea un split posible en el árbol. |
| `PreferredPaymentMode` | 5 | 5 | Idem. `handle_unknown='ignore'` protege ante categorías nuevas en producción (ninguna apareció en este test, pero es buena práctica). |
| `Gender` | 2 | 2 | Idem. |
| `PreferedOrderCat` | 5 | 5 | **Mayor asociación categórica con churn** (Cramér's V 0,226). |
| `MaritalStatus` | 3 | 3 | Cardinalidad baja, sin orden. |

Decisión confirmada con el usuario: `drop=None` (vs `drop='first'`) porque el modelo principal del TP es **árbol de decisión + Random Forest** — para ellos `drop=None` no introduce multicolinealidad problemática y mantiene cada categoría observable en SHAP. Si después se prueba LogReg, se puede componer un pipeline alternativo con `drop='first'`.

**Total dummies categóricas:** 2 + 5 + 2 + 5 + 3 = **17 columnas**.

### Binarias — passthrough

| Variable | Tratamiento |
|---|---|
| `Complain` | Sin transformar (ya 0/1). |

---

## 5 · Features derivadas

Las tres se calculan **después** del pipeline para que `Tenure` ya esté
imputada y la flag/banderas reflejen la versión "completa" del dato.

| Feature nueva | Fórmula | Técnica BA | Hipótesis del EDA |
|---|---|---|---|
| `Tenure_was_na` | `df_raw['Tenure'].isna().astype(int)` | #6 condicional / flag de missingness | Sospecha de missingness informativa en el predictor #1. Si el null no es aleatorio, esta flag captura la señal residual de "no estar registrado". Media en train ≈ 4,7%. |
| `tenure_bajo_queja` | `((Tenure_imputed <= 3) & (Complain == 1)).astype(int)` | #6 condicional | Operacionaliza H2 (`EDA hipótesis.md`): la queja del cliente nuevo dispara churn (OR=21,7 con Tenure≤1; con Tenure≤3 captura una ventana operativamente útil de "primer trimestre"). Media en train ≈ 9,2%. **Tasa de churn dentro de esta flag = 66,0%** (vs 11,8% fuera). |
| `citytier_alto_queja` | `((CityTier > 1) & (Complain == 1)).astype(int)` | #6 condicional | Operacionaliza el patrón observado en H4: la queja en tiers no-1 eleva el churn. Aunque el efecto focalizado tier 2/3 vs tier 1 no fue significativo (p=0,176), la flag combina dos variables con señal independiente — útil para que el árbol corte en una sola decisión. Media en train ≈ 10,2%. |

**Naming:** se mantienen los nombres pedidos por el usuario en el prompt (snake_case en español), consistentes con la convención del proyecto.

---

## 6 · Lista completa de features de salida

Orden de columnas (33 features + `Churn`):

```
Numéricas continuas escaladas (9):
  Tenure, WarehouseToHome, HourSpendOnApp, NumberOfAddress,
  OrderAmountHikeFromlastYear, CouponUsed, OrderCount,
  DaySinceLastOrder, CashbackAmount

Ordinales escaladas (3):
  CityTier, SatisfactionScore, NumberOfDeviceRegistered

OHE PreferredLoginDevice (2):
  PreferredLoginDevice_Computer, PreferredLoginDevice_Mobile Phone

OHE PreferredPaymentMode (5):
  PreferredPaymentMode_COD, PreferredPaymentMode_Credit Card,
  PreferredPaymentMode_Debit Card, PreferredPaymentMode_E wallet,
  PreferredPaymentMode_UPI

OHE Gender (2):
  Gender_Female, Gender_Male

OHE PreferedOrderCat (5):
  PreferedOrderCat_Fashion, PreferedOrderCat_Grocery,
  PreferedOrderCat_Laptop & Accessory, PreferedOrderCat_Mobile Phone,
  PreferedOrderCat_Others

OHE MaritalStatus (3):
  MaritalStatus_Divorced, MaritalStatus_Married, MaritalStatus_Single

Binaria passthrough (1):
  Complain

Flag de missingness (1):
  Tenure_was_na

Features derivadas (2):
  tenure_bajo_queja, citytier_alto_queja

Target (1):
  Churn
```

**Total: 33 features + 1 target = 34 columnas.**

---

## 7 · Verificaciones (Fase 6 — Verify)

Ejecutadas sobre los parquets generados:

| Check | Resultado |
|---|---|
| Split antes de cualquier `fit` | ✅ confirmado en `run_pipeline()` |
| `fit_transform` solo en train, `transform` solo en test | ✅ |
| Train + Test = 5.630 filas | ✅ 4.504 + 1.126 |
| Mismas columnas en train y test | ✅ |
| Estratificación: tasa de churn similar | ✅ 16,83% train · 16,87% test |
| Nulos en parquets de salida | ✅ 0 en ambos |
| Sanity check RobustScaler (mediana train = 0) | ✅ todas las numéricas escaladas con mediana exacta 0 en train |
| OHE: suma de dummies por grupo = 1 en cada fila | ✅ en las 5 categóricas |
| Features derivadas en {0, 1} | ✅ |
| `tenure_bajo_queja=1` reproduce señal del EDA | ✅ 66,0% churn vs 11,8% fuera del segmento |
| Reproducibilidad (`random_state=42` fijado) | ✅ |
| No se hizo feature selection | ✅ (es del Modeler) |

---

## 8 · Warnings para el Modeler

1. **`Complain` puede ser leakage temporal** (heredado del Explorer). Sigue presente en el parquet. **Entrená el modelo con y sin esta columna** y reportá el delta de recall. Si la diferencia es chica, retirá la variable por prudencia defensiva.
2. **`DaySinceLastOrder` tiene signo contraintuitivo** (rank-biserial -0,29: los que se quedan tienen *más* días sin comprar). Pedile al área de negocio la definición exacta antes de interpretarla en el reporte ejecutivo. Para el modelo no es bloqueante.
3. **`tenure_bajo_queja` y `citytier_alto_queja` son derivadas de `Tenure` y `Complain`** → si decidís dropear `Complain` por leakage, también drop a estas dos flags. Hacen las dos cosas: comparten la misma dependencia.
4. **`Tenure_was_na` activa para ~4,7% de los clientes**. Verificá en la matriz de importancia/SHAP si esta flag aporta. Si no, dropea — no agrega ruido pero tampoco señal.
5. **OHE con `drop=None`** introduce multicolinealidad perfecta dentro de cada grupo. **Sin impacto para árboles/RF**; **sí impacta** si querés probar LogReg o regularización L2 estricta — en ese caso, recompone el pipeline cambiando a `drop='first'`.
6. **3 features sin señal en EDA**: `HourSpendOnApp` (p=0,23), `CouponUsed` (p=0,27), `OrderAmountHikeFromlastYear` (p=0,13). Quedan en el dataset; el árbol decide. Si no las usa: documentar en `decisions.md` que la elección de mantenerlas fue para evitar sesgo del analista.
7. **No se hizo feature selection.** Es la siguiente etapa del Modeler.

---

## 9 · Reproducibilidad

Para regenerar los parquets:

```bash
.venv/bin/python -m src.features.pipeline
```

Para usar el pipeline en el notebook de modelado:

```python
from src.features.pipeline import run_pipeline

train_df, test_df, y_train, y_test, preprocessor = run_pipeline()
# o cargar los parquets ya escritos:
import pandas as pd
train = pd.read_parquet("data/processed/features_train.parquet")
test = pd.read_parquet("data/processed/features_test.parquet")
y_train = train.pop("Churn")
y_test = test.pop("Churn")
```

`build_pipeline()` devuelve el `ColumnTransformer` **sin fitear**, listo para
componer con un clasificador dentro de un `Pipeline` mayor (útil si el
Modeler quiere fitear todo en un `GridSearchCV`).
