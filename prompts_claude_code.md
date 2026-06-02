# Prompts para Claude Code — Semana 1

Enfocados en lo que pide la **Semana 1**: setup + entender el negocio + *formular* hipótesis (sin validar ni modelar todavía).
Flujo de la cátedra: **Entender → Delegar → Validar**, con los subagentes del `data-science-kit` (`ds-planner`, `ds-explorer`) y `grill-me`.

> En cada prompt: pedí **2–3 alternativas antes de ejecutar**, elegí con criterio de negocio y registrá la decisión en `decisions.md`. Si un concepto no te cierra, frená y usá `grill-me`.

---

## 0 · Instalar las skills (una sola vez)
- `data-science-kit` (subagentes `ds-planner` / `ds-explorer`): https://github.com/agus-chaud/data-science-kit
- `grill-me`: https://skills.sh/mattpocock/skills/grill-me
- `gentle-ai` (Engram + voz criolla + sdd-flow): https://github.com/Gentleman-Programming/gentle-ai

En Claude Code, las skills van en `.claude/skills/` (del proyecto) o `~/.claude/skills/` (global). Instalá según el README de cada repo y verificá con `/skills`. Después abrí Claude Code **dentro de `tp-churn-ecommerce/`**.

---

## PROMPT 1 · Setup + subir TODA la Fase 1 a GitHub  ⬅️ el primero
```
Sos mi copiloto técnico para la Semana 1 de un TP de "IA Aplicada a Negocios" (predicción de churn).
Mi rol es de negocio, no de programador: yo entiendo y decido, vos ejecutás y me explicás.
Objetivo de este prompt: dejar TODA la Fase 1 lista y subida a GitHub.

Hacé esto y explicame cada paso en lenguaje simple:
1. Verificá/creá la estructura del repo: data/raw, notebooks, reports, src + README.md, requirements.txt y .gitignore.
2. Confirmá el entorno: que el entorno virtual esté activo y estén instaladas las dependencias
   (pandas, numpy, scikit-learn, matplotlib, seaborn, scipy, jupyter, openpyxl).
3. Chequeá que las skills estén instaladas (data-science-kit, grill-me) y listá las disponibles.
4. Cargá data/raw/E_Commerce_Dataset.xlsx (hoja "E Comm") en un notebook y mostrá df.head() y df.shape.
   Confirmá también que la hoja "Data Dict" tiene el diccionario de variables.
5. Hacé el primer commit y push a GitHub. ANTES de pushear, mostrame git status y el mensaje de commit
   propuesto y esperá mi OK.

Checkpoints de la cátedra (no avances si alguno falla): entorno virtual activo, df.head() corre, primer commit hecho.
```

## PROMPT 2 · Entendimiento del negocio (las 3 preguntas)
```
Antes de tocar a fondo los datos, ayudame a responder por escrito (en reports/00_entendimiento_negocio.md),
con mentalidad de negocio y pensando en la ACCIÓN, no en el dato puro:
1. ¿Qué es churn y por qué le importa económicamente a la empresa? (usá que es ~17% sobre 5.630 clientes)
2. ¿Qué significa que adquirir un cliente nuevo cuesta 5–7 veces más que retener uno?
3. ¿Qué decisión concreta va a tomar el gerente comercial con mi análisis?
Dame primero un borrador, marcá los supuestos que estás haciendo, y después cuestioná mis respuestas como
si fueras el gerente (¿y esto en plata qué significa? ¿qué hago el lunes con esto?).
```

## PROMPT 3 · Explorar señales y formular hipótesis (con ds-explorer)
```
Usá el subagente ds-explorer sobre data/raw (sin modificar el original). Quiero un perfilado rápido y, sobre todo,
TASAS DE CHURN POR SEGMENTO para fundamentar hipótesis de negocio: por antigüedad (Tenure), quejas, satisfacción,
estado civil, ciudad, categoría preferida, método de pago, y algunas INTERACCIONES con "cliente nuevo" (Tenure<=1).

No me des el output crudo. Proponeme un MENÚ de 8-12 hipótesis candidatas, cada una con: el dato que la respalda,
la lógica de negocio y la ACCIÓN concreta que habilitaría. Mi foco es frenar el churn temprano. No valides todavía
con tests (eso es Semana 2); esto es formulación. Cuando lo tengas, ayudame a elegir 5 que cubran palancas distintas.
```

## PROMPT 4 · Notebook mínimo de Semana 1
```
Armá un notebook notebooks/00_semana1.ipynb que: (a) cargue los datos y muestre df.head() y la tasa de churn global,
(b) para cada una de mis 5 hipótesis elegidas, haga UN gráfico simple (barras) que la muestre y debajo una
interpretación en lenguaje de negocio con la acción que sugiere. Nada de tests estadísticos ni modelos todavía.
Mantenelo legible para alguien de negocio. Antes de codear, decime qué gráfico propondrías para cada hipótesis y por qué.
```

---

## Antes de cerrar la semana: `grill-me`
```
Usá la skill grill-me. Interrogame hasta que pueda explicar sin leer: qué es churn y por qué importa en plata,
por qué el primer mes es crítico, qué es el desbalance de clases y por qué la accuracy va a engañar, y por qué una
hipótesis "obvia" (como la de satisfacción) hay que validarla y no asumirla. No me dejes pasar respuestas flojas.
```

---

### Recordatorio de alcance
Semana 1 = setup + entender + formular. **Modelado, métricas, SHAP y reporte ejecutivo son Semanas 2 y 3** — no los adelantes acá (aunque tengamos material, lo dejamos para cuando corresponda).
