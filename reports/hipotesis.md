# Hipótesis — Validación estadística

**Fecha:** 2026-06-05
**Dataset:** `data/raw/E_Commerce_Dataset.xlsx` (hoja `E Comm`) · n = 5.630 · churn rate global = 16,84%
**α de referencia:** 0,05

Cada hipótesis tiene **enunciado · test · resultado numérico · interpretación
de negocio · recomendación para el modelo**. Los gráficos están en
`reports/figures/`. La formulación original (Semana 1) está en
`reports/01_hipotesis.md`; este documento la valida formalmente.

> 📖 Cuando el test asume normalidad y se viola (n grande + sesgo), priorizamos
> tests no paramétricos. Para variables ordinales/binarias usamos Mann-Whitney
> U, Chi-cuadrado y Spearman, todos con tamaño de efecto reportado
> (rank-biserial, Cramér's V, ρ). Marco inferencial alineado con la skill
> `ds-stats`.

---

## H1 · El riesgo de fuga se concentra en clientes nuevos (Tenure bajo)

**Enunciado.** Los clientes con antigüedad baja (especialmente en el primer
mes) tienen una tasa de churn sustancialmente mayor que los establecidos.

**Test aplicado.**
- **Mann-Whitney U** (no paramétrico, unilateral H₁: `Tenure(no-churn) > Tenure(churn)`).
  Justificación: `Tenure` está fuertemente sesgada (skew = 0,74, KS rechaza
  normalidad con p ≈ 10⁻⁶⁴); n grande; comparamos dos grupos independientes.
  Mann-Whitney compara distribuciones sin asumir forma.
- **Chi-cuadrado** sobre la tabla `TenureBucket × Churn` (con cortes 0-1m,
  2-3m, 4-6m, 7-12m, 13-24m, >24m) para cuantificar la asociación discreta.

**Resultado.**
| Métrica | Valor |
|---|---|
| Mann-Whitney U | 3.185.639 |
| p-valor (unilateral) | 2,84 × 10⁻¹⁹³ |
| Rank-biserial (tamaño de efecto) | **-0,633** (grande) |
| χ² sobre buckets | 1.464,1 · p ≈ 0 · Cramér's V = **0,522** (grande) |

Tasas de churn por bucket de antigüedad:

| Bucket | n | Churn |
|---|---:|---:|
| **0–1 m** | 1.198 | **51,84%** |
| 2–3 m | 362 | 8,84% |
| 4–6 m | 590 | 7,46% |
| 7–12 m | 1.320 | 5,68% |
| 13–24 m | 1.467 | 6,48% |
| > 24 m | 429 | **0,00%** |

**Gráfico:** [`figures/h1_tenure_buckets.png`](figures/h1_tenure_buckets.png)

**Interpretación de negocio.** El primer mes de vida del cliente concentra
brutalmente el riesgo: **uno de cada dos clientes nuevos se va**, contra ~6%
en el resto del año. Después de dos años, la fuga prácticamente no existe
en los datos. La ventana de intervención de retención es corta y temprana.

**Recomendación para el modelo.**
- Mantener `Tenure` como feature numérica (no la transformes en categórica
  primero; un árbol partirá donde corresponde).
- Crear adicionalmente `EsNuevo = (Tenure ≤ 1)` como bandera explícita —
  ayuda al árbol a aislar el segmento de mayor riesgo en un solo nodo.
- Para SHAP: esperar que `Tenure` (o `EsNuevo`) sea el feature dominante.

---

## H2 · Cliente nuevo + queja = casi una baja segura (interacción)

**Enunciado.** Un reclamo dentro del primer mes dispara el churn mucho más
que el mismo reclamo en un cliente con antigüedad. Hipótesis de interacción.

**Test aplicado.**
- **Chi-cuadrado** sobre `(EsNuevo × Complain) × Churn` (tabla 4 × 2 con los
  4 grupos: nuevo-sin-queja, nuevo-con-queja, establecido-sin-queja,
  establecido-con-queja). Mide la asociación global.
- **Fisher exacto unilateral** comparando "nuevo + queja" contra "el resto".
  Más robusto cuando hay celdas pequeñas; nos da el **odds ratio**.

**Resultado.**
| Métrica | Valor |
|---|---|
| χ² (4 grupos) | 1.728,8 |
| p-valor χ² | ≈ 0 |
| Cramér's V | **0,568** (grande) |
| Odds ratio (nuevo+queja vs resto) | **21,7** |
| Fisher p (unilateral) | 2,65 × 10⁻¹⁷⁸ |

Tasas de churn por celda:

|  | Sin queja | Con queja |
|---|---:|---:|
| **Establecido (>1 m)** | 3,57% | 12,51% |
| **Nuevo (≤1 m)** | 39,36% | **72,87%** |

El n del grupo "nuevo + queja" es 446 (suficiente para no ser ruido).

**Gráfico:** [`figures/h2_tenure_complain.png`](figures/h2_tenure_complain.png)

**Interpretación de negocio.** Combinar las dos peores condiciones (cliente
sin vínculo + queja) lleva la tasa de churn al **73%** — casi 20 veces la
del cliente establecido sin queja (3,6%). La queja temprana no es un mal
día: es el preludio de una baja.

**Recomendación para el modelo.**
- Construir la interacción explícita `EsNuevo × Complain` como feature
  (un árbol la captura sin ayuda, pero la interacción explícita es útil
  para modelos lineales y para SHAP).
- Caveat de leakage: si `Complain` sale del modelo (ver H7 del data
  quality), esta interacción también sale.
- Implementación de negocio (no del modelo): la queja del primer mes debe
  disparar una alerta de retención **inmediata**, antes de cualquier
  predicción.

---

## H3 · La satisfacción declarada NO protege del churn (contraintuitiva)

**Enunciado.** El score de satisfacción no sirve como termómetro de
retención. En clientes nuevos, los "muy satisfechos" se van **igual o más**
que los insatisfechos.

**Test aplicado.**
- **Chi-cuadrado** `SatisfactionScore × Churn` restringido a clientes nuevos
  (Tenure ≤ 1). Justificación: la pregunta es sobre nuevos; medir en todo
  el dataset diluye el efecto con el bloque de "establecidos".
- **Spearman ρ** entre `SatisfactionScore` y `Churn` en nuevos. Si el
  termómetro funciona, ρ debería ser claramente negativa. Si ρ es ~0 o
  positiva, la hipótesis contraintuitiva queda confirmada.

**Resultado (sólo nuevos, n = 1.198).**
| Métrica | Valor |
|---|---|
| χ² | 26,11 |
| p-valor χ² | 3,0 × 10⁻⁵ |
| Cramér's V | 0,148 (pequeño-medio) |
| **Spearman ρ** | **+0,141** |
| p-valor Spearman | 9,7 × 10⁻⁷ |

Tasas de churn por SatisfactionScore (sólo nuevos):

| Score | n | Churn |
|---|---:|---:|
| 1 | 217 | 41,5% |
| 2 | 116 | 41,4% |
| 3 | 361 | 52,6% |
| 4 | 202 | 53,0% |
| **5** | 302 | **61,6%** |

Como referencia, en el dataset completo el patrón es el mismo (más suave):
score 1 = 11,1%, score 5 = 22,6%.

**Gráfico:** [`figures/h3_satisfaction_nuevos.png`](figures/h3_satisfaction_nuevos.png)

**Interpretación de negocio.** Confirmada y notable. **El score de
satisfacción correlaciona POSITIVAMENTE con churn en clientes nuevos**:
los "muy satisfechos" (score 5) se van al 61,6%, contra 41,5% de los
"insatisfechos" (score 1). El termómetro no solo no detecta el riesgo —
sugiere lo contrario.

Hipótesis sobre el mecanismo (para validar con negocio): el score puede
estar capturando "expectativa" más que "satisfacción real". Un nuevo que
declara satisfacción 5 quizás expresa entusiasmo inicial frágil; uno con
score 1 viene curtido y ya tolera fricciones. **No es una conclusión, es
una hipótesis para que el área de CX investigue.**

**Recomendación para el modelo.**
- Conservar la variable: aporta señal, aunque sea en dirección no
  intuitiva.
- Para el reporte ejecutivo: vender como hallazgo contraintuitivo
  ("validar antes de asumir"). No confiar en el score como métrica de
  alarma temprana.
- Revisar con el área cómo y cuándo se mide el score (¿al onboarding?
  ¿después de una compra? ¿NPS-style?).

---

## H4 · Tier 2/3 + queja peor que Tier 1 + queja (interacción)

**Enunciado.** Los clientes en ciudades de menor tier abandonan más, y una
queja en esas ciudades es **aún más letal** que la misma queja en Tier 1.

**Test aplicado.**
- **Chi-cuadrado global** sobre los 6 grupos `(CityTier × Complain) × Churn`
  para confirmar que el patrón conjunto existe.
- **Chi-cuadrado focalizado** comparando `Tier 2/3 con queja` vs `Tier 1 con
  queja` para validar la afirmación específica de la hipótesis.

**Resultado.**
| Métrica | Valor |
|---|---|
| χ² global (6 grupos) | 397,6 |
| p global | 9,8 × 10⁻⁸⁴ |
| Cramér's V global | 0,266 (medio) |
| **χ² focalizado** (Tier 2/3 + queja vs Tier 1 + queja) | 1,83 |
| **p focalizado** | **0,176** |
| Cramér's V focalizado | 0,068 (despreciable) |
| n Tier 2/3 con queja | 560 |
| n Tier 1 con queja | 1.044 |

Tasas de churn por celda:

|  | Tier 1 | Tier 2 | Tier 3 |
|---|---:|---:|---:|
| Sin queja | 9,0% | 15,6% | 14,4% |
| Con queja | 28,4% | 32,3% | 38,6% |

**Gráfico:** [`figures/h4_citytier_complain.png`](figures/h4_citytier_complain.png)

**Interpretación de negocio (con honestidad estadística).**

Hay **dos efectos por separado** y son sólidos:
- **Tier importa:** tier 3 churnea más que tier 1 (15,6% vs 9,0% sin queja).
- **Queja importa muchísimo:** la queja triplica la tasa en cualquier tier.

Pero la afirmación **específica** de H4 — que la queja en tier 2/3 es
**más letal** que la queja en tier 1 — no es estadísticamente
significativa al α = 0,05. Visualmente sí se ve (38,6% vs 28,4%), pero
con n=560 vs n=1.044, ese delta entra dentro del ruido. La hipótesis
está **parcialmente confirmada**: el patrón de tendencia existe; la
diferencia puntual entre las dos zonas no se puede afirmar con esta
muestra.

**Recomendación para el modelo.**
- Conservar `CityTier` como feature categórica ordinal. Tiene señal por
  sí sola.
- Conservar `Complain`. Tiene señal por sí sola (con caveat de leakage).
- La interacción `CityTier × Complain` puede aparecer en el árbol como
  una rama natural; no es imprescindible engineerla.

**Recomendación para el reporte ejecutivo.**
- Sí decir: "fuera de Tier 1, el churn es más alto y la queja es la
  palanca más peligrosa".
- **No decir:** "una queja en el interior es peor que una queja en la
  capital", a menos que se haga la comparación dentro del segmento de
  clientes nuevos (donde la muestra alcanza para conclusiones más
  firmes).

---

## H5 · Más dispositivos registrados = más churn (contraintuitiva)

**Enunciado.** Cuantos más dispositivos tiene asociados un cliente, más
probable es que se vaya. Va contra la intuición de "más dispositivos = más
enganche".

**Test aplicado.**
- **Chi-cuadrado** `NumberOfDeviceRegistered × Churn` (asociación global).
- **Spearman ρ** para confirmar tendencia monotónica.
- **Mann-Whitney U** unilateral (H₁: `devices(churn) > devices(no-churn)`)
  como test direccional con tamaño de efecto.

**Resultado.**
| Métrica | Valor |
|---|---|
| χ² | 81,11 |
| p-valor χ² | 4,9 × 10⁻¹⁶ |
| Cramér's V | 0,120 (pequeño-medio) |
| **Spearman ρ** | **+0,101** |
| p-valor Spearman | 2,6 × 10⁻¹⁴ |
| Mann-Whitney p (unilateral) | 1,5 × 10⁻¹⁴ |
| Rank-biserial | +0,148 |

Tasas de churn por cantidad de dispositivos:

| Dispositivos | n | Churn |
|---|---:|---:|
| 1 | 235 | 9,36% |
| 2 | 276 | 9,42% |
| 3 | 1.699 | 14,95% |
| 4 | 2.377 | 16,49% |
| 5 | 881 | 22,47% |
| **6** | 162 | **34,57%** |

**Gráfico:** [`figures/h5_devices.png`](figures/h5_devices.png)

**Interpretación de negocio.** Confirmada. El patrón es monotónicamente
creciente: de 9,4% (1-2 dispositivos) a 34,6% (6 dispositivos). Tres
interpretaciones posibles para el área (no se puede afirmar cuál con estos
datos):
1. **Cuentas compartidas** (varios dispositivos = familia/grupo, menor
   compromiso individual).
2. **"Shopping around":** el cliente que compara precios en muchos lados
   también se va a otros lados.
3. **Confusión técnica:** problemas para acceder genera más
   re-registros desde dispositivos nuevos (frustración → churn).

**Recomendación para el modelo.**
- Conservar `NumberOfDeviceRegistered` como feature numérica.
- El "tamaño de efecto" es modesto (Cramér's V = 0,12; ρ = 0,10), así que
  no es un predictor estrella — pero es señal consistente.
- Para el negocio: investigar el cluster de 5-6 dispositivos como cohorte
  específica antes de actuar.

---

## Tabla resumen para el Modeler

| Hip. | Verdadera | Tamaño de efecto | Variable involucrada | Mantener en modelo |
|---|---|---|---|---|
| H1 | ✅ Sí | Grande (rank-biserial -0,63) | `Tenure` + `EsNuevo` | Sí (predictor #1) |
| H2 | ✅ Sí | Grande (OR = 21,7; V = 0,57) | `EsNuevo × Complain` | Sí (con caveat de leakage) |
| H3 | ✅ Sí (contraintuitiva) | Pequeño-medio (V = 0,15) | `SatisfactionScore` | Sí — no descartar por intuición |
| H4 | ⚠️ Parcialmente | Global medio, focal NO significativo | `CityTier`, `Complain` | Sí ambas por separado |
| H5 | ✅ Sí (contraintuitiva) | Pequeño-medio (V = 0,12; ρ = 0,10) | `NumberOfDeviceRegistered` | Sí |
