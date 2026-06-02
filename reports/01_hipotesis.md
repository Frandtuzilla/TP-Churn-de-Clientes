# Semana 1 — Hipótesis de negocio (formulación)

Cinco hipótesis formuladas con **lógica de negocio**, elegidas con un foco: **frenar el churn temprano y poder accionar sobre eso**.
Cada una trae su lógica, una **señal preliminar** en los datos (para no elegir a ciegas) y la **acción de negocio** que habilitaría.

> **Alcance Semana 1:** acá *formulamos* y mostramos cada hipótesis con un gráfico simple e interpretación de negocio.
> La **validación formal** (test estadístico + control de confusores) es de Semana 2. Los % son una primera lectura.

---

## H1 · El riesgo de fuga se concentra en el primer mes
**Enunciado:** los clientes nuevos (antigüedad baja) tienen un riesgo de irse muchísimo mayor que los establecidos.
**Lógica de negocio:** todavía no hay hábito de compra ni costo de cambio percibido; el vínculo es frágil.
**Señal preliminar:** 0–1 mes = **51,8%** de churn; cae a ~6% entre los 2 y 12 meses y a **0%** pasados los 2 años.
**Acción que habilita:** programa de onboarding intensivo en los primeros 30 días (es la intervención de mayor retorno).
**Gráfico:** % de churn por tramo de antigüedad.

## H2 · Una queja de un cliente NUEVO es casi una baja segura ⭐ (interacción)
**Enunciado:** un reclamo en los primeros 30 días dispara el churn mucho más que el mismo reclamo de un cliente con antigüedad.
**Lógica de negocio:** el cliente sin vínculo no perdona un mal primer trato; la queja temprana es una herida sin anestesia.
**Señal preliminar:** *nuevo + queja = 72,9%* de churn, contra 39% del nuevo sin queja (y solo 16% del que se queja pero ya tiene antigüedad).
**Acción que habilita:** prioridad máxima a las quejas de clientes con menos de 30 días (respuesta y seguimiento exprés).
**Gráfico:** churn por queja, separando cliente nuevo vs. resto.

## H3 · La satisfacción declarada NO protege del churn ⭐ (contraintuitiva)
**Enunciado:** el score de satisfacción no sirve como termómetro de retención; incluso los "muy satisfechos" se van.
**Lógica de negocio:** lo que la gente declara y lo que hace no coinciden; un score alto puede dar una falsa tranquilidad y tapar el riesgo real.
**Señal preliminar:** score 5 = **23,8%** de churn, *mayor* que score 1 = **11,5%**.
**Acción que habilita:** dejar de usar el score como termómetro de retención y revisar cómo/cuándo se mide; basar la alerta en comportamiento (antigüedad, quejas), no en encuestas.
**Gráfico:** churn por SatisfactionScore (1–5).

## H4 · En tier 2 y 3 se churnea más — y ahí las quejas pegan más fuerte ⭐ (interacción)
**Enunciado:** los clientes de ciudades de menor tier abandonan más, y una queja en esas ciudades es aún más letal.
**Lógica de negocio:** peor experiencia logística (entregas más lentas/caras, menos cobertura) fuera de las grandes ciudades amplifica el efecto de un mal servicio.
**Señal preliminar:** Tier 3 = **21,4%** y Tier 2 = 19,8% vs. Tier 1 = **14,5%**; y *Tier 3 + queja = 38,6%* (vs. 28,4% en Tier 1).
**Acción que habilita:** reforzar servicio y tiempos de entrega en tier 2/3, y priorizar la atención de quejas en esas zonas.
**Gráfico:** churn por tier de ciudad, y churn por tier separando con/sin queja.

## H5 · Más dispositivos registrados = más riesgo ⭐ (contraintuitiva)
**Enunciado:** cuantos más dispositivos tiene asociados un cliente, más probable es que se vaya.
**Lógica de negocio:** contra la intuición de "más enganchado". Muchos dispositivos puede indicar **cuentas compartidas** o **"shopping around"** (el que compara precios en varios lados es menos fiel).
**Señal preliminar:** 1–2 dispositivos ≈ **9%** de churn vs. 5 dispositivos = 22,5% y **6 dispositivos = 34,6%**.
**Acción que habilita:** investigar señales de multicuenta y comportamiento de comparación; no asumir que más actividad = más lealtad.
**Gráfico:** churn por cantidad de dispositivos registrados.

---

### Por qué estas cinco (criterio de negocio)
Cubren palancas distintas y cuentan una historia coherente alrededor del **churn temprano**:
- **H1** pone el escenario: el primer mes es el campo de batalla.
- **H2 y H4** son **interacciones** que muestran *dónde* y *cuándo* el riesgo se dispara (la queja del nuevo, la queja en tier 2/3) → acciones quirúrgicas.
- **H3 y H5** son **contraintuitivas**: demuestran que **validamos en vez de asumir** (un score alto no salva; más dispositivos no fideliza). Es lo que más suma en la defensa.

### Banco de hipótesis descartadas (por si querés cambiar alguna)
Quedaron en el menú (`00_hipotesis_candidatas.md`): blindaje del primer año, soltero nuevo, categoría de entrada, método de pago, app vs. computadora y distancia al depósito.
