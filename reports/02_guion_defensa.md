# Guión de defensa — Semana 2
**Proyecto:** Churn de Clientes — E-Commerce
**Actualizado:** 2026-06-10

---

## 1. Glosario de términos (analogías de calle)

**Churn rate**
La tasa de clientes que se fueron en un período. Si tenés 100 clientes hoy y 17 se
fueron este mes, tu churn rate es 17%. En el dataset: 16,84% del total.

**α (alfa) y nivel de confianza**
El umbral de tolerancia al error. α = 0,05 significa: "acepto equivocarme 1 de cada
20 veces cuando digo que algo es real". El nivel de confianza es el complemento:
95%. No es magia, es un acuerdo de cuánta incertidumbre tolerás antes de actuar.

**p-valor**
La probabilidad de ver un resultado tan extremo como el que observaste *si en
realidad no hubiera ninguna diferencia*. Analogía de calle: tirás una moneda 10 veces
y sale cara 9 veces. El p-valor te dice "¿qué tan raro es esto si la moneda fuera
justa?". Si ese número es muy chico (p < 0,05), empezás a sospechar que la moneda
está cargada. **Lo que NO dice el p-valor:** qué tan grande es el efecto ni si
importa en el negocio. Para eso están los tamaños de efecto.

**Tamaño de efecto**
El p-valor dice "¿hay algo?"; el tamaño de efecto dice "¿cuánto?". Con n = 5.630
casi todo da significativo. Un p ≈ 0 con Cramér's V = 0,05 es estadísticamente
real pero prácticamente irrelevante. Siempre reportar los dos.

**Mann-Whitney U (y por qué en vez de t-test)**
El t-test compara promedios asumiendo que los datos siguen una distribución normal
— como si midiera la altura de personas adultas, donde todo se distribuye en
campana. Mann-Whitney no asume nada de eso: trabaja con *rankings* (ordenás todos
los valores de menor a mayor y comparás dónde caen cada grupo). Analogía: si querés
saber si los ricos llegan antes que los pobres a un destino, no necesitás saber la
distribución exacta de sus velocidades; solo ordenás los tiempos de llegada y mirás.
En este proyecto, `Tenure` tiene fuerte sesgo (skew = 0,74, con el pico en el primer
mes y una cola larga) y el test de Kolmogorov-Smirnov rechaza normalidad con
p ≈ 10⁻⁶⁴. El t-test daría resultados no confiables. Mann-Whitney es la elección
correcta.

**Rank-biserial (ej: -0,633 de H1)**
El tamaño de efecto de Mann-Whitney. Va de -1 a +1. Interpretación directa: si tomás
un cliente churneado y un cliente que se quedó y los comparás en Tenure, el
rank-biserial de -0,633 dice que en el 63,3% de los pares posibles, el churneado
tiene *menor* antigüedad que el que se quedó. Dicho en calle: "en 6 de cada 10
comparaciones, el que se fue era más nuevo". El signo negativo refleja la dirección
del test (H₁: Tenure del no-churn > Tenure del churn). Convención de magnitud:
|r| ≥ 0,5 es efecto grande.

**Cramér's V (ej: 0,568 de H2)**
El tamaño de efecto para chi-cuadrado. Va de 0 a 1. Mide qué tan fuerte es la
asociación entre dos variables categóricas, independientemente del tamaño de la
tabla. V = 0 es "no hay relación"; V = 1 es "conociendo una variable, sabés la
otra con certeza". Convención práctica: < 0,10 despreciable; 0,10-0,30 pequeño;
0,30-0,50 medio; > 0,50 grande. El 0,568 de H2 (interacción tenure × queja) entra
en categoría grande: la combinación "cliente nuevo + queja" predice el churn con
mucha fuerza. Comparar: V = 0,148 de H3 (satisfaction) es pequeño-medio — hay
señal pero menos potente.

**Spearman ρ (rho)**
Mide si dos variables tienen una relación monotónica: cuando una sube, ¿la otra
siempre sube también (o siempre baja)? No exige que la relación sea una línea recta
como Pearson, solo que tenga dirección consistente. Trabaja con rangos, igual que
Mann-Whitney. En H3: Spearman ρ = +0,141 entre SatisfactionScore y Churn en
clientes nuevos. El signo positivo confirma lo contraintuitivo: a más satisfacción
declarada, más churn. En H5: ρ = +0,101 entre dispositivos y churn — relación
pequeña pero monotónicamente creciente (siempre hacia arriba). Convención de
magnitud: |ρ| < 0,10 débil; 0,10-0,30 moderado; > 0,30 fuerte.

**Odds Ratio (ej: OR 21,7 de H2)**
Compara las chances de que algo ocurra entre dos grupos. Odds de churn en grupo A
dividido por odds de churn en grupo B. OR = 1 → igual riesgo. OR > 1 → el grupo A
tiene más riesgo. OR = 21,7 de H2 significa: un cliente nuevo con queja tiene 21,7
veces más chances de churnearse que el resto. En lenguaje de gerente: "de cada 100
clientes que no están en esa situación y se van, hay 2.170 que están en esa
situación y se van". No es difícil de vender en una reunión. Importante: OR ≠
probabilidad. OR = 21,7 no es "21 veces más probable"; es 21 veces más *chances*
(que en la práctica, cuando la probabilidad base es alta, se traduce en un número
enorme de casos reales).

**RobustScaler vs StandardScaler**
Ambos transforman variables numéricas para que estén en una escala comparable y los
modelos no sufran por diferencias de magnitud. La diferencia está en cómo calculan
la "escala":
- *StandardScaler* usa la media y el desvío estándar. Problema: un outlier
  extremo arrastra la media y el desvío, distorsionando toda la escala. Como
  recalcular el precio por metro cuadrado de una ciudad incluyendo el Palacio de
  Buckingham.
- *RobustScaler* usa la mediana y el rango intercuartílico (IQR: diferencia entre
  el percentil 75 y el 25). Estos estadísticos no se mueven con outliers. En este
  proyecto, `Tenure` y otras variables continuas tienen distribuciones sesgadas;
  RobustScaler es la elección defensiva correcta.

---

## 2. Resultados de hipótesis — Semana 2

### H1 · El riesgo de fuga se concentra en clientes nuevos (Tenure bajo) ✅

| Métrica | Valor |
|---|---|
| Test | Mann-Whitney U (no paramétrico, unilateral) |
| p-valor | 2,84 × 10⁻¹⁹³ |
| Rank-biserial | **-0,633** (efecto grande) |
| χ² sobre buckets de Tenure | 1.464,1 · p ≈ 0 · Cramér's V = **0,522** (grande) |

Tasas de churn por antigüedad:

| Bucket | Churn |
|---|---:|
| 0–1 mes | **51,84%** |
| 2–3 meses | 8,84% |
| 4–6 meses | 7,46% |
| 7–12 meses | 5,68% |
| 13–24 meses | 6,48% |
| > 24 meses | **0,00%** |

**Conclusión:** el primer mes concentra el riesgo de forma brutal. Uno de cada dos
clientes nuevos se va. La ventana de intervención es corta y temprana.

---

### H2 · Cliente nuevo + queja = casi una baja segura (interacción) ✅

| Métrica | Valor |
|---|---|
| Cramér's V (4 grupos) | **0,568** (grande) |
| Odds Ratio (nuevo+queja vs resto) | **21,7** |
| Fisher p (unilateral) | 2,65 × 10⁻¹⁷⁸ |

Tasas de churn por celda:

|  | Sin queja | Con queja |
|---|---:|---:|
| Establecido (> 1 mes) | 3,57% | 12,51% |
| **Nuevo (≤ 1 mes)** | 39,36% | **72,87%** |

**Conclusión:** combinar cliente nuevo + queja lleva el churn al 73%. La queja
temprana no es un mal día: es el preludio de una baja. OR = 21,7 — casi 22 veces
más chances de irse que el resto.

---

### H3 · La satisfacción declarada NO protege del churn (contraintuitiva) ✅

| Métrica | Valor |
|---|---|
| Spearman ρ (solo nuevos) | **+0,141** |
| p-valor Spearman | 9,7 × 10⁻⁷ |
| Cramér's V | 0,148 (pequeño-medio) |

Tasas de churn por score (solo clientes nuevos, n = 1.198):

| Score | Churn |
|---|---:|
| 1 (insatisfecho) | 41,5% |
| 2 | 41,4% |
| 3 | 52,6% |
| 4 | 53,0% |
| **5 (muy satisfecho)** | **61,6%** |

**Conclusión:** el score de satisfacción correlaciona *positivamente* con churn en
clientes nuevos. Los "muy satisfechos" se van más. El termómetro no solo no detecta
el riesgo — apunta en la dirección contraria. La variable se conserva en el modelo
(tiene señal), pero no sirve como alerta temprana.

---

### H4 · Tier 2/3 + queja peor que Tier 1 + queja ⚠️ Parcialmente confirmada

| Métrica | Valor |
|---|---|
| χ² global (6 grupos) | 397,6 · p ≈ 0 · Cramér's V = 0,266 (medio) |
| **χ² focalizado** (Tier 2/3+queja vs Tier 1+queja) | 1,83 |
| **p focalizado** | **0,176** (no significativo) |
| Cramér's V focalizado | 0,068 (despreciable) |

Tasas de churn por celda:

|  | Tier 1 | Tier 2 | Tier 3 |
|---|---:|---:|---:|
| Sin queja | 9,0% | 15,6% | 14,4% |
| Con queja | 28,4% | 32,3% | 38,6% |

**Conclusión:** los efectos individuales de CityTier y Complain son sólidos por
separado. Pero la afirmación específica de que la queja en Tier 2/3 es *más letal*
que la misma queja en Tier 1 no alcanza significancia estadística (p = 0,176). El
patrón de tendencia existe visualmente; con esta muestra no se puede afirmar la
diferencia puntual entre zonas. Ambas variables se conservan en el modelo por
separado.

---

### H5 · Más dispositivos registrados = más churn (contraintuitiva) ✅

| Métrica | Valor |
|---|---|
| Cramér's V | 0,120 (pequeño-medio) |
| Spearman ρ | **+0,101** |
| Rank-biserial | +0,148 |

Tasas de churn por dispositivos: 9,4% (1-2) → 14,9% (3) → 16,5% (4) → 22,5% (5)
→ **34,6% (6)**. Patrón monotónicamente creciente.

**Conclusión:** confirmada con efecto modesto pero consistente. Cuantos más
dispositivos, más churn — contrario a la intuición de "más enganche". Variable se
conserva en el modelo.

---

## 3. Preguntas filosas para preparar la defensa

---

**"Tu H4 salió p = 0,176, ¿por qué la presentás?"**

Porque la honestidad estadística *es* un resultado. H4 tiene dos partes: el efecto
global (CityTier y Complain por separado) es sólido y significativo — Cramér's V
= 0,266 con p ≈ 0. Lo que no es significativo es la afirmación *específica* de que
la queja en el interior golpea peor que la misma queja en la capital. Presentar ese
matiz muestra que el análisis no busca confirmar hipótesis sino testearlas. Además,
el patrón de tendencia (28,4% → 38,6%) existe: con más datos o restringiendo al
segmento de clientes nuevos, podría alcanzar significancia. Ocultar esto sería peor
que mostrarlo.

---

**"¿Por qué el score de satisfacción correlaciona positivamente con churn?"**

No lo sabemos con certeza, y eso hay que decirlo. Tenemos tres hipótesis de
mecanismo que el área de CX debería investigar:

1. **Expectativa frágil:** el cliente nuevo que pone 5 puede estar expresando
   entusiasmo inicial alto, no satisfacción consolidada. Cuando la realidad no
   cumple esa expectativa, se va.
2. **Cortesía vs compromiso:** un cliente que ya decidió irse puede declarar score
   alto para evitar confrontación en la encuesta ("qué bueno todo, chau").
3. **Sesgo de timing:** si el score se mide al comienzo del onboarding y el churn
   ocurre semanas después, puede capturar un estado transitorio.

Lo que sí podemos afirmar: la variable tiene señal estadística real (p = 9,7 × 10⁻⁷)
y en dirección no intuitiva. No se descarta del modelo. Pero no se usa como alerta
temprana de retención.

---

**"¿Qué es un Odds Ratio de 21,7 en lenguaje de gerente?"**

Si tomás a todos los clientes que *no* son nuevos con queja y mirás cuántos se van:
eso es tu línea de base. Ahora tomás a los clientes nuevos con queja: tienen 21,7
veces más *chances* de irse que esa línea de base. En términos concretos: la tasa de
churn de ese grupo es 72,87% contra 3,57% del establecido sin queja. Cada 100
clientes nuevos que presentan una queja en el primer mes, aproximadamente 73 se van.
El costo de no intervenir en ese segmento es directo y cuantificable: si el ticket
promedio mensual es X, multiplicalo por 73 clientes perdidos por cada 100 con esa
combinación.

---

**"¿Por qué Mann-Whitney y no t-test?"**

El t-test asume que los datos se distribuyen normalmente (en campana). `Tenure` tiene
skew = 0,74 con un pico enorme en el primer mes y una cola que se arrastra hasta los
60 meses. El test de Kolmogorov-Smirnov rechaza la normalidad con p ≈ 10⁻⁶⁴ — no
hay ambigüedad. En esa situación, el t-test daría un resultado técnicamente
incorrecto porque sus supuestos no se cumplen. Mann-Whitney trabaja con rankings: no
necesita que los datos tengan forma de campana, solo que sean comparables por orden.
Es el test correcto para esta distribución. Dicho de otra forma: el t-test le creería
demasiado al promedio, que en `Tenure` está inflado por la cola larga; Mann-Whitney
le cree al percentil del medio (mediana), que es un resumen más honesto de dónde
está concentrada la mayoría de los datos.
