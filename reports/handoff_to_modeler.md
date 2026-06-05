# Handoff · Explorer → Modeler

**Fecha:** 2026-06-05
**Dataset:** `data/raw/E_Commerce_Dataset.xlsx` · hoja `E Comm` · 5.630 filas · 20 columnas
**Target:** `Churn` (binario · 1 = se fue · 0 = se quedó)
**Detalles completos:** `reports/eda.md` · `reports/hipotesis.md` · `reports/data_quality.md`

---

## 1. Desbalance del target

| Clase | n | % |
|---|---:|---:|
| 0 (se quedó) | 4.682 | 83,16% |
| 1 (se fue) | 948 | 16,84% |
| Ratio minoritaria / mayoritaria | — | 0,202 |

**Estrategia sugerida:**
- `train_test_split(..., stratify=y, test_size=0.2, random_state=42)` antes de
  cualquier transformación.
- `class_weight='balanced'` o `'balanced_subsample'` en el árbol y el RF.
- Considerar mover el umbral de decisión por debajo de 0,5 si el negocio
  prioriza recall (sale natural si optimizamos PR-AUC).
- SMOTE solo si los modelos con `class_weight` no rinden — agrega complejidad
  y no siempre mejora.

---

## 2. Métrica recomendada

**Métrica principal: Recall.**
**Métricas de soporte: Precision · PR-AUC · F1 · matriz de confusión.**
**Excluida explícitamente: Accuracy.**

**Justificación.**
- El costo de perder un cliente (5-7× o más el costo de retener) supera al
  costo de una intervención innecesaria. El recall mide qué proporción de los
  que se iban realmente detectamos.
- Con 16,84% de churn, "predecir siempre 0" da 83% de accuracy → métrica
  inútil.
- PR-AUC es preferible a ROC-AUC para datasets desbalanceados (refleja mejor
  el comportamiento en la clase minoritaria).

---

## 3. Variables sospechosas de leakage

| Variable | Severidad | Razón | Acción |
|---|---|---|---|
| `Complain` | Media-alta | "Queja del último mes" — sin fecha exacta. Si se registra al cancelar, ve el futuro. χ² con churn p ≈ 10⁻⁷⁸. | Entrenar dos modelos: con `Complain` (principal) y sin `Complain` (control). Comparar recall. Confirmar mecanismo con negocio. |

**No detectadas otras formas de leakage:**
- Ninguna feature numérica tiene |r| > 0,5 con el target.
- Ningún campo binario coincide >95% con `Churn`.

---

## 4. Columnas a dropear (antes de modelar)

| Columna | Razón |
|---|---|
| `CustomerID` | Identificador, no aporta señal predictiva. |

**No se dropean** variables por baja señal (`HourSpendOnApp`,
`CouponUsed`, `OrderAmountHikeFromlastYear`). Mantenerlas — el árbol
decide; el feature importance dirá si son irrelevantes.

---

## 5. Encodings sugeridos por columna

### Categóricas nominales
| Columna | Cardinalidad | Encoding sugerido | Justificación |
|---|---:|---|---|
| `Gender` | 2 | `OneHotEncoder(drop='first')` o LabelEncoder binario | Trivial. |
| `PreferredLoginDevice` | 2 | OneHot | Trivial. |
| `PreferredPaymentMode` | 5 | OneHot | Cardinalidad chica; OneHot mantiene interpretabilidad para el árbol y el reporte. |
| `PreferedOrderCat` | 5 | OneHot | Cardinalidad chica; **feature de alta señal** (Cramér's V = 0,226). |
| `MaritalStatus` | 3 | OneHot | Cardinalidad chica; señal media (V = 0,183). |

> Categorías ya unificadas en `src/data_prep.py:clean_categories`: `Phone →
> Mobile Phone`; `CC → Credit Card`; `Cash on Delivery → COD`; `Mobile →
> Mobile Phone`. Confirmar que el pipeline carga la versión limpia.

### Numéricas ordinales (dejar como están)
| Columna | Razón |
|---|---|
| `CityTier` | Ordinal 1-3, ya numérico. |
| `SatisfactionScore` | Ordinal 1-5, ya numérico. |
| `NumberOfDeviceRegistered` | Ordinal 1-6, ya numérico. |

### Numéricas continuas
| Columna | Tratamiento |
|---|---|
| `Tenure`, `WarehouseToHome`, `HourSpendOnApp`, `NumberOfAddress`, `OrderAmountHikeFromlastYear`, `CouponUsed`, `OrderCount`, `DaySinceLastOrder`, `CashbackAmount` | Mantener escala. Imputar con mediana **dentro del pipeline**, ajustado solo con train. Para Random Forest/árbol no hace falta escalar; si se compara con Logistic Regression, `StandardScaler` post-imputación. |

### Binarias
| Columna | Tratamiento |
|---|---|
| `Complain` | Ya 0/1, no tocar. (Pero ver §3 — leakage.) |

---

## 6. Features que conviene crear (feature engineering, no exploración)

| Feature | Definición | Por qué |
|---|---|---|
| `EsNuevo` | `(Tenure <= 1).astype(int)` | El feature de mayor poder predictivo (H1: 51,8% churn en este segmento vs 4-7% en el resto). El árbol la inventaría; explicitarla hace el modelo más legible. |
| `NuevoYQueja` | `EsNuevo & Complain` | Interacción de H2 con OR=21,7. Útil para SHAP y para reportes. |

> No engineer adicional: el Explorer no diseña features productivas. Estas
> dos son banderas obvias que respetan el espíritu de "EDA no transforma para
> producción" porque son operacionalizaciones directas de hallazgos del EDA.

---

## 7. Imputación de nulos

| Columna | Nulos | % | Imputación sugerida |
|---|---:|---:|---|
| `DaySinceLastOrder` | 307 | 5,45% | Mediana (3,0) |
| `OrderAmountHikeFromlastYear` | 265 | 4,71% | Mediana (15,0) |
| `Tenure` | 264 | 4,69% | Mediana (9,0) — **considerar marcar `Tenure_was_na`** porque es el predictor #1 |
| `OrderCount` | 258 | 4,58% | Mediana (2,0) |
| `CouponUsed` | 256 | 4,55% | Mediana (1,0) |
| `HourSpendOnApp` | 255 | 4,53% | Mediana (3,0) |
| `WarehouseToHome` | 251 | 4,46% | Mediana (14,0) |

**Regla dura:** la imputación va **dentro** del pipeline `sklearn`, ajustada
**solo con train**. Imputar antes del split filtra información del test.

---

## 8. Variables con señal confirmada

| Variable | Test | p-valor | Tamaño de efecto | Prioridad |
|---|---|---|---|---|
| `Tenure` | Mann-Whitney (H1) | 10⁻¹⁹³ | rank-biserial -0,633 | **Alta** |
| `Complain` | χ² | 10⁻⁷⁸ | Cramér's V 0,250 | **Alta** (con caveat de leakage) |
| `EsNuevo × Complain` (interacción) | Fisher exacto (H2) | 10⁻¹⁷⁸ | OR 21,7 | **Alta** |
| `PreferedOrderCat` | χ² | 10⁻⁶¹ | Cramér's V 0,226 | Alta |
| `MaritalStatus` | χ² | 10⁻⁴¹ | Cramér's V 0,183 | Media |
| `DaySinceLastOrder` | Mann-Whitney | 10⁻⁴² | rank-biserial -0,287 | Media (ojo: el signo no coincide con la intuición — chequear definición con negocio) |
| `CashbackAmount` | Mann-Whitney | 10⁻³⁸ | rank-biserial -0,266 | Media (asociación monotónica, ver `eda.md` §5) |
| `SatisfactionScore` | χ² (H3) | 10⁻⁵ en nuevos | Cramér's V 0,148 | Media (contraintuitiva — ρ positiva con churn) |
| `NumberOfDeviceRegistered` | χ² (H5) | 10⁻¹⁶ | Cramér's V 0,120 | Media (contraintuitiva) |
| `CityTier` | χ² | 10⁻⁸⁴ | Cramér's V 0,266 | Media |
| `PreferredPaymentMode` | χ² | 10⁻¹⁰ | Cramér's V 0,096 | Media |
| `WarehouseToHome` | Mann-Whitney | 10⁻⁹ | rank-biserial 0,127 | Baja-media |
| `NumberOfAddress` | Mann-Whitney | 0,030 | rank-biserial 0,044 | Baja |
| `PreferredLoginDevice` | χ² | 10⁻⁴ | Cramér's V 0,051 | Baja |
| `Gender` | χ² | 0,031 | Cramér's V 0,029 | Baja |

---

## 9. Variables sin señal (después de 2+ encodings o tests)

| Variable | Tests intentados | p-valor más alto | Conclusión |
|---|---|---|---|
| `HourSpendOnApp` | Mann-Whitney, point-biserial, KS por grupo | 0,23 | Sin señal a nivel global. Llevar al modelo, pero esperar que el árbol no la use. |
| `CouponUsed` | Mann-Whitney, point-biserial | 0,27 | Idem. |
| `OrderAmountHikeFromlastYear` | Mann-Whitney, point-biserial | 0,13 | Idem. |

Decisión: **conservar en el modelo**. El árbol las descartará por feature
importance si efectivamente no aportan. No descartarlas a mano nos da una
prueba honesta de su irrelevancia.

---

## 10. Warnings importantes para el Modeler

1. **NO IMPUTAR ANTES DEL SPLIT.** Toda imputación va dentro de un
   `Pipeline` o `ColumnTransformer`, ajustada con `fit` solo en train.
2. **NO ESCALAR ANTES DEL SPLIT.** Mismo motivo.
3. **`Complain` puede ser leakage.** Reportar métricas con y sin esta
   variable. Si la diferencia de recall es chica, retirarla por prudencia
   defensiva.
4. **`Tenure` es el predictor #1.** Si el modelo tiene AUC > 0,99,
   auditar: ¿es por `Tenure` (legítimo) o por `Complain` (sospechoso)?
   Mirar feature importance / SHAP.
5. **`DaySinceLastOrder` tiene signo contraintuitivo.** Pedir definición
   exacta al área antes de interpretarla en el reporte ejecutivo.
6. **No usar accuracy como métrica principal.** El baseline "predecir 0
   siempre" da 83%; el modelo debe medirse contra eso en recall y PR-AUC,
   no en accuracy.
7. **Validación cruzada estratificada k=5** para que el resultado no sea
   suerte. Confidence interval por fold.

---

## 11. Baseline obligatorio

`DummyClassifier(strategy="most_frequent")` o equivalente. Es el piso de
comparación: cualquier modelo que no le gane en recall es un modelo
mal hecho (no un fracaso del problema).

| Métrica esperada del baseline | Valor aprox. |
|---|---|
| Accuracy | 83% |
| Recall (clase 1) | 0% |
| Precision (clase 1) | 0% (división por cero, manejar con `zero_division=0`) |
| PR-AUC | ≈ tasa base (0,168) |

---

## 12. Próximos pasos sugeridos

1. Split estratificado.
2. Pipeline con `SimpleImputer(strategy='median')` + `OneHotEncoder` para
   nominales.
3. Baseline `DummyClassifier`.
4. Árbol de decisión (`max_depth` 3-5 para interpretabilidad +
   `class_weight='balanced'`).
5. Random Forest como comparación.
6. (Opcional) Regresión logística con `StandardScaler` para tener una
   comparativa lineal.
7. Cross-validation estratificada k=5.
8. Métricas: recall, precision, F1, PR-AUC, ROC-AUC, matriz de confusión.
9. Comparativa con y sin `Complain`.
10. SHAP global + local (mínimo 3 casos: nuevo+queja, establecido sin queja,
    nuevo sin queja).

---

## 13. Feature Engineering — Resultado Final  *(actualizado 2026-06-05)*

> Los pasos 1, 2 de §12 ya están **resueltos** por el pipeline de features.
> El Modeler arranca directamente desde los parquets.

**Artefactos disponibles:**

| Archivo | Descripción |
|---|---|
| `data/processed/features_train.parquet` | 4.504 filas × 33 features + `Churn` — transformaciones aplicadas (mediana imputada con TRAIN, RobustScaler ajustado con TRAIN, OHE ajustado con TRAIN) |
| `data/processed/features_test.parquet` | 1.126 filas × 33 features + `Churn` — solo `transform`, sin `fit` |
| `src/features/pipeline.py` | Pipeline reproducible: `build_pipeline()` (sin fitear) + `run_pipeline()` (orquesta split+fit+transform) |
| `reports/feature_report.md` | Documentación completa de cada transformación |

**Split:**
- 80% train / 20% test · `stratify=y` · `random_state=42`
- Train: 4.504 filas · churn 16,83%
- Test: 1.126 filas · churn 16,87%

**Shape final:** 33 features (12 numéricas escaladas + 17 dummies OHE + 1
binaria + 1 flag de null + 2 derivadas) + `Churn`.

### Features disponibles para evaluación (decisión final = Modeler)

```
[Numéricas continuas escaladas]
Tenure · WarehouseToHome · HourSpendOnApp · NumberOfAddress ·
OrderAmountHikeFromlastYear · CouponUsed · OrderCount ·
DaySinceLastOrder · CashbackAmount

[Numéricas ordinales escaladas]
CityTier · SatisfactionScore · NumberOfDeviceRegistered

[OHE PreferredLoginDevice]
PreferredLoginDevice_Computer · PreferredLoginDevice_Mobile Phone

[OHE PreferredPaymentMode]
PreferredPaymentMode_COD · PreferredPaymentMode_Credit Card ·
PreferredPaymentMode_Debit Card · PreferredPaymentMode_E wallet ·
PreferredPaymentMode_UPI

[OHE Gender]
Gender_Female · Gender_Male

[OHE PreferedOrderCat]
PreferedOrderCat_Fashion · PreferedOrderCat_Grocery ·
PreferedOrderCat_Laptop & Accessory · PreferedOrderCat_Mobile Phone ·
PreferedOrderCat_Others

[OHE MaritalStatus]
MaritalStatus_Divorced · MaritalStatus_Married · MaritalStatus_Single

[Binarias y derivadas]
Complain · Tenure_was_na · tenure_bajo_queja · citytier_alto_queja
```

### Cómo cargar en el notebook 02_modelado.ipynb

```python
import pandas as pd
train = pd.read_parquet("data/processed/features_train.parquet")
test  = pd.read_parquet("data/processed/features_test.parquet")
y_train = train.pop("Churn")
y_test  = test.pop("Churn")
X_train, X_test = train, test
```

O — si querés componerlo con un clasificador dentro de un `Pipeline` único
(útil para `GridSearchCV`):

```python
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from src.features.pipeline import build_pipeline

clf = Pipeline([
    ("features", build_pipeline()),
    ("model", DecisionTreeClassifier(class_weight="balanced", random_state=42)),
])
# fitear sobre el raw post-split (X_train_raw, y_train) — pipeline.py hace
# el resto de las transformaciones. Igual conviene levantar los parquets
# para la mayoría de los entrenamientos.
```

### Recomendaciones específicas para el Modeler

1. **Empezar con TODAS las features.** Dejá que la importancia del árbol / RF haga selection. No descartar a mano (sesgo del analista).
2. **Modelo con/sin `Complain` (obligatorio).** Si dropeás `Complain`, droppeá también `tenure_bajo_queja` y `citytier_alto_queja` (dependen de la misma variable).
3. **Cross-validation estratificada k=5.** Reportá métricas como media ± std, no un único número.
4. **Métricas:** recall (prioritaria), PR-AUC, F1, precision, ROC-AUC. **Accuracy queda excluida.**
5. **Umbral de decisión.** El default 0,5 está optimizado para accuracy. Para priorizar recall, mover el umbral por debajo de 0,5 — reportá la curva precision-recall.
6. **Atención a `NumberOfAddress`** (no aparecía en los warnings del Explorer): es la única numérica continua sin nulls que no tiene señal fuerte (rank-bis 0,04). Si el árbol la usa mucho, sospechoso.
7. **Reproducibilidad.** Si reentrenás algo, ejecutá `python -m src.features.pipeline` desde el root del repo. El `random_state=42` está fijado en `pipeline.py`.

### Verificaciones que ya pasó el pipeline

✅ Split antes de cualquier `fit`
✅ Imputación y escalado fiteados solo con train
✅ Estratificación correcta (train 16,83% vs test 16,87%)
✅ 0 nulos en los parquets de salida
✅ OHE consistente (suma = 1 por grupo en cada fila)
✅ Features derivadas reproducen la señal del EDA (`tenure_bajo_queja=1` → 66,0% churn)
✅ No se hizo feature selection (es del Modeler)
