# Semana 1 — Entendimiento del problema (negocio antes que datos)

Tres preguntas que hay que responder *antes* de tocar el dataset. La idea no es definir términos de manual, sino dejar claro **qué decisión de plata hay detrás**.

---

## 1. ¿Qué es churn y por qué le importa económicamente a la empresa?

**Churn** es el cliente que deja de comprarnos — el que "se borra". En nuestro caso, el año pasado se fue cerca del **17% de la base**: sobre 5.630 clientes, son **~948 clientes perdidos en un año**.

Por qué importa en plata:
- **Ingreso recurrente que se evapora.** Cada cliente que se va deja de generar ventas y margen, mes a mes.
- **Hay que reemplazarlo, y reemplazar es caro** (ver punto 2). El churn no es "neutro": obliga a gastar para volver al punto de partida.
- **Cortás el valor futuro (LTV).** Los clientes que se quedan tienden a comprar más con el tiempo; perder uno temprano te corta todo ese valor que todavía no cobraste.
- **Efecto compuesto.** Por eso unos pocos puntos de retención mueven mucho la rentabilidad: una mejora del 5% en retención puede subir las ganancias entre 25% y 95%.

En una frase para el gerente: *cada punto de churn que bajamos es margen que se queda en casa y que, además, crece con el tiempo.*

---

## 2. ¿Qué significa que adquirir un cliente nuevo cuesta 5–7 veces más que retener uno?

Significa que **la misma plata rinde mucho más cuidando a los clientes que ya tenemos que persiguiendo nuevos** (en e-commerce la brecha llega a 5–25×).

- **Captar** carga con marketing, descuentos de adquisición, costo de conversión, anuncios.
- **Retener** se juega con acciones más baratas: buena experiencia, una respuesta rápida a una queja, un beneficio puntual y bien dirigido.
- Por cada $1 que invertís en retener, evitás gastar $5–7 en adquisición solo para quedar igual.

Conclusión de negocio: **un presupuesto de retención bien apuntado (a los de mayor riesgo y mayor valor) es de los gastos con mejor retorno de la empresa.** Repartirlo a ciegas o reaccionar tarde es tirar plata.

---

## 3. ¿Qué decisión concreta va a tomar el gerente comercial con tu análisis?

El análisis no termina en un número: termina en **tres decisiones operativas**.

- **¿A quién intervenir?** Una lista de clientes en riesgo, priorizando a los del **primer mes** y a los perfiles de alto riesgo que vamos a identificar (por ejemplo: el cliente nuevo que se quejó, el soltero nuevo, ciertas categorías de entrada).
- **¿Con qué recursos?** Cómo repartir el presupuesto de retención: **concentrarlo donde el riesgo y el valor son altos**, en vez de gastar lo mismo en todos.
- **¿Cuándo y cómo actuar?** El *timing* (los primeros 30 días son críticos) y la *palanca* adecuada para cada caso: onboarding, respuesta prioritaria a quejas, empujar un método de pago más comprometido, etc.

El objetivo final: pasar de *"perdemos el 17% y nos enteramos tarde"* a *"detectamos temprano y actuamos con foco, midiendo el retorno"*.

---

> **Hilo conductor de todo el TP:** el riesgo de fuga se concentra brutalmente en el **primer mes de vida del cliente** (más de la mitad de los nuevos se va). Todo lo que sigue —hipótesis, modelo y recomendaciones— apunta a *detectar y frenar ese churn temprano*, porque es donde está la plata y donde la acción llega a tiempo.
