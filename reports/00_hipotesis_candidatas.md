# Menú de hipótesis candidatas — Semana 1

**Cómo usar este documento:** elegí **5** (o modificá las que quieras) marcando con una `X`. Cada hipótesis trae:
la **señal en los datos** (mirada preliminar, para que esté fundamentada), la **lógica de negocio** y, lo más importante,
**la acción que habilita** — porque el objetivo no es el dato, sino la decisión que permite tomar.

> Nota: en Semana 1 *formulamos* las hipótesis con su lógica. La **validación formal** (test estadístico + gráfico prolijo) es de Semana 2. Los % de abajo son una primera lectura para no elegir a ciegas.

---

## A · Ciclo de vida / onboarding
- [ ] **1. El riesgo de fuga se concentra en el primer mes.**
  *Datos:* 0–1 mes = **51,8%** de churn; cae a ~6% entre los 2–12 meses y a **0%** pasados los 2 años.
  *Negocio:* todavía no hay hábito ni costo de cambio. *Acción:* programa de onboarding intensivo en los primeros 30 días.
- [ ] **2. Cruzar el primer año "blinda" al cliente.**
  *Datos:* después de 24 meses el churn es prácticamente nulo. *Negocio:* la lealtad se construye temprano. *Acción:* incentivos puente (beneficio al mes 3, 6 y 12) para empujar al cliente a cruzar ese umbral.

## B · Servicio, quejas y satisfacción
- [ ] **3. Una queja triplica la probabilidad de irse.**
  *Datos:* quejó = **31,7%** vs. no quejó = **10,9%**. *Negocio:* la queja es la bandera roja más accionable. *Acción:* protocolo de recuperación post-reclamo con seguimiento.
- [ ] **4. Una queja de un cliente NUEVO es casi una baja segura.** ⭐ (interacción)
  *Datos:* nuevo + queja = **72,9%** de churn (vs. 39% nuevo sin queja). *Negocio:* el cliente sin vínculo no perdona un mal primer trato. *Acción:* dar prioridad máxima a las quejas de clientes con < 30 días.
- [ ] **5. La satisfacción declarada NO protege del churn.** ⭐ (contraintuitiva)
  *Datos:* score 5 = **23,8%** de churn > score 1 = **11,5%**. *Negocio:* el "está satisfecho" puede ser un falso tranquilizante. *Acción:* dejar de usar el score de satisfacción como termómetro de retención y revisar cómo/ cuándo se mide.

## C · Segmentos demográficos
- [ ] **6. Los solteros se van mucho más que los casados.**
  *Datos:* Single = **26,7%** vs. Married = **11,5%**; y un **soltero nuevo = 61,7%**. *Negocio:* menos "anclas" de consumo familiar. *Acción:* onboarding y ofertas diferenciadas por estado civil.
- [ ] **7. Las ciudades tier 2 y 3 churnean más — y ahí las quejas pegan más fuerte.** ⭐ (interacción)
  *Datos:* Tier 3 = **21,4%** vs. Tier 1 = 14,5%; Tier 3 + queja = **38,6%**. *Negocio:* peor experiencia/logística fuera de las grandes ciudades. *Acción:* reforzar servicio y tiempos de entrega en tier 2/3.

## D · Producto / categoría
- [ ] **8. La categoría preferida predice fuerte el churn.**
  *Datos:* Mobile Phone = **27,4%** y Fashion (nuevos = **78%**) vs. **Grocery = 4,9%**. *Negocio:* las categorías "de hobby" o de compra única retienen menos. *Acción:* expectativas y recompra a medida por categoría.
- [ ] **9. Las categorías de consumo habitual generan hábito (y retención).**
  *Datos:* Grocery = 4,9% de churn (el más bajo de todos). *Negocio:* lo que se consume seguido crea rutina. *Acción:* empujar una primera compra de consumibles para instalar el hábito.

## E · Pago y canal (señales de compromiso)
- [ ] **10. El medio de pago señala el nivel de compromiso.**
  *Datos:* COD = **24,9%** y e-wallet = 22,8% vs. Credit Card = **14,2%**. *Negocio:* pagar contra entrega = vínculo más laxo y reversible. *Acción:* incentivar métodos "atados" (tarjeta guardada, débito).
- [ ] **11. Quien usa la app móvil se queda más que quien entra por computadora.**
  *Datos:* Computer = **19,8%** vs. Mobile = 15,6%. *Negocio:* la app genera más enganche (notificaciones, fricción baja). *Acción:* impulsar la adopción de la app.

## F · Comportamiento / uso
- [ ] **12. Más dispositivos registrados = más riesgo.** ⭐ (contraintuitiva)
  *Datos:* 1–2 dispositivos ≈ **9%** vs. 6 dispositivos = **34,6%**. *Negocio:* podría indicar cuentas compartidas o "shopping around" comparando precios. *Acción:* revisar señales de multicuenta y comportamiento de comparación.
- [ ] **13. La distancia al depósito mete fricción y empuja al churn.**
  *Datos:* 20–35 km = **20,5%** vs. < 10 km = 13,5%. *Negocio:* envíos más lentos/caros. *Acción:* mejorar logística (o subsidiar envío) en zonas alejadas.

---

### ✍️ Mis 5 elegidas
1. **#1** — El riesgo se concentra en el primer mes.
2. **#4** — La queja de un cliente nuevo es casi una baja segura. ⭐
3. **#5** — La satisfacción declarada NO protege del churn. ⭐ (contraintuitiva)
4. **#7** — Tier 2 y 3 churnean más, y ahí las quejas pegan más fuerte. ⭐
5. **#12** — Más dispositivos registrados = más riesgo. ⭐ (contraintuitiva)

→ Versión desarrollada en `01_hipotesis.md`.

> Tip de negocio: una buena selección **cubre palancas distintas** (p. ej. una de onboarding, una de servicio, una de segmento, una de producto y una "contraintuitiva" que demuestre que validás y no asumís). Eso te da un relato más rico para la defensa.
