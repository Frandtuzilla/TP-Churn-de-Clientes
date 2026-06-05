# Calidad de datos — E Commerce Churn

**Fecha:** 2026-06-05
**Dataset:** `data/raw/E_Commerce_Dataset.xlsx` (hoja `E Comm`)
**Shape:** 5.630 filas × 20 columnas · 2,4 MB en memoria

---

## 1. Inventario rápido

| Métrica | Valor |
|---|---|
| Filas | 5.630 |
| Columnas | 20 (1 ID + 1 target + 18 features) |
| Tipos | 5 categóricas (`object`) · 8 enteras · 7 flotantes |
| Duplicados exactos (con CustomerID) | 0 |
| Duplicados ignorando CustomerID | **557 pares** (1.114 filas involucradas; ningún grupo > 2) |
| Filas con al menos un nulo | 1.405 (≈25%) |

> **Sobre los duplicados.** Hay 557 pares de filas idénticas en todas las features pero con `CustomerID` distinto. Es esperable: la mayoría de las variables son discretas y de baja cardinalidad (`CityTier∈{1,2,3}`, `Complain∈{0,1}`, `SatisfactionScore∈{1..5}`, `NumberOfDeviceRegistered∈{1..6}`, etc.) y muchas tienen nulos en posiciones que también coinciden. **No es error de carga**: son clientes distintos con perfiles que colisionan por azar. No se dropean — el modelo los ve como observaciones independientes (lo son).

---

## 2. Nulos por columna

| Columna | Nulos | % | Tipo |
|---|---:|---:|---|
| `DaySinceLastOrder` | 307 | 5,45% | float64 |
| `OrderAmountHikeFromlastYear` | 265 | 4,71% | float64 |
| `Tenure` | 264 | 4,69% | float64 |
| `OrderCount` | 258 | 4,58% | float64 |
| `CouponUsed` | 256 | 4,55% | float64 |
| `HourSpendOnApp` | 255 | 4,53% | float64 |
| `WarehouseToHome` | 251 | 4,46% | float64 |
| Resto (13 columnas) | 0 | 0% | — |

**Patrón:** 7 columnas concentran TODOS los nulos, todas numéricas continuas, todas en el rango 4,4–5,5%. Distribución muy parecida ⇒ posible mecanismo común (¿registro incompleto en clientes con menos historia? Las que tienen nulos son justamente variables de actividad).

**Decisión sugerida (post-split):** imputación por mediana dentro de pipeline `sklearn`. El % es bajo y la mediana es robusta a las distribuciones sesgadas que vimos (skew alto en `WarehouseToHome`, `CouponUsed`, `OrderCount`). **No imputar antes del split** — contamina el test.

---

## 3. Columnas constantes / cuasi-constantes

Ninguna columna constante ni con ≥99% una misma categoría. Todas aportan variabilidad.

---

## 4. Inconsistencias de etiquetas (ya corregidas en `src/data_prep.py`)

| Columna | Mapping | Razón |
|---|---|---|
| `PreferredLoginDevice` | `Phone` → `Mobile Phone` | Misma categoría escrita distinto |
| `PreferredPaymentMode` | `CC` → `Credit Card`, `Cash on Delivery` → `COD` | Idem |
| `PreferedOrderCat` | `Mobile` → `Mobile Phone` | Idem (ojo: el nombre de la columna también está con typo en el dataset original) |

Sin unificar, el modelo trataría a `Phone` y `Mobile Phone` como categorías distintas y se diluiría la señal. Los `value_counts` finales son los de la versión limpia.

---

## 5. Outliers (regla IQR 1.5)

| Variable | Outliers | % | Lectura |
|---|---:|---:|---|
| `OrderCount` | 703 | 12,49% | Cola larga típica de conteos (skew 2,2). Naturales, no errores. |
| `CouponUsed` | 629 | 11,17% | Misma lógica (skew 2,5). |
| `CashbackAmount` | 438 | 7,78% | Cola por clientes premium. |
| `NumberOfDeviceRegistered` | 397 | 7,05% | Aparecen como "outliers" porque la mediana cae justo en el centro (3-4) y la regla IQR los marca; **no son anomalías**, son los grupos pequeños de 1, 2, 5 y 6 dispositivos. |
| `DaySinceLastOrder` | 62 | 1,10% | Cola moderada. |
| `OrderAmountHikeFromlastYear` | 33 | 0,59% | Mínima. |
| `WarehouseToHome` | 2 | 0,04% | **Pero el `max` = 127 km con mediana 14 — revisar si es plausible**. |
| Resto | 0–6 | <0,1% | — |

**Casos para mirar individualmente:**
- `WarehouseToHome` `max = 127`: lejos del p99. Si la unidad es km, plausible solo para casos extremos rurales. **Sugerencia:** dejar como está pero clipear/winsorizar en el pipeline si el modelo se sensibiliza.
- `Tenure` `max = 61` meses (5 años). Coherente.

**Regla general:** no eliminar outliers en EDA. Reportarlos. La decisión de winsorizar/transformar va en el pipeline del Modeler.

---

## 6. Variable sospechosa de leakage: `Complain`

| Detalle | Valor |
|---|---|
| Tipo | Binaria (0/1) |
| Distribución | 28,5% de clientes con queja |
| Churn cuando `Complain=1` | 31,67% |
| Churn cuando `Complain=0` | 10,93% |
| Diferencia | **+20,74 pp** |
| χ² independencia con `Churn` | p = 2,7×10⁻⁷⁸ |
| Cramér's V | 0,250 (efecto medio) |

**Por qué es sospechosa:** el diccionario describe `Complain` como "queja en el último mes" — sin fecha exacta. Si el reclamo se registra **después** de que el cliente decidió irse (queja de cancelación, escalamiento al darse de baja), usar la variable equivale a "ver el futuro". El modelo levantaría una señal que no estará disponible al momento de predecir.

**Recomendación operativa (Modeler):**
1. Mantener `Complain` en el modelo principal y reportar métricas con y sin ella, midiendo el delta de recall.
2. Si el delta es chico, considerar retirarla por prudencia y para defender el modelo ante el gerente.
3. Confirmar con negocio: ¿la queja se registra al recibirla, o al darse de baja? La respuesta cambia todo.

---

## 7. Otras señales que el Modeler debe saber

- **Desbalance del target:** 83,16% no-churn vs 16,84% churn (ratio ≈ 1:5). Importante para elegir métrica (recall, precision, PR-AUC) y eventualmente `class_weight='balanced'`.
- **`Tenure` es la variable más asociada al target** (|r|=0,35; rango muy amplio 0–61 meses, sesgo positivo). Conserva la escala numérica si el modelo lo aprovecha; para el árbol, puede ser conveniente además una variable binaria `EsNuevo = (Tenure ≤ 1)`.
- **Variables sin señal** (después de Mann-Whitney): `HourSpendOnApp` (p=0,23), `CouponUsed` (p=0,27), `OrderAmountHikeFromlastYear` (p=0,13). Llevarlas al modelo pero sin esperar mucho de ellas; podrían ser candidatas a drop si el árbol no las usa.
- **`PreferedOrderCat`** tiene la **mayor asociación categórica con churn** (Cramér's V = 0,226). `Mobile Phone` es la categoría con más churn (27,4%) y `Grocery` la de menos (4,9%). Variable clave para el modelo.
- **`MaritalStatus`** también pesa (Cramér's V = 0,183). `Single` se va al 26,7% vs `Married` 11,5%.
