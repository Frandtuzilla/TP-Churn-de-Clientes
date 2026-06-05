# TP — Predicción de Churn de Clientes

Proyecto de la materia **Inteligencia Artificial Aplicada a Negocios** (Lic. en Negocios y Tecnología).

**Objetivo:** anticipar qué clientes de un e-commerce están por irse (churn) y entender por qué, para habilitar decisiones de retención. El foco está en el criterio de negocio y la capacidad de explicar y defender cada decisión, no en la precisión del modelo.

## Dataset
- 5.630 clientes, 20 columnas (1 ID + 1 target + 18 features).
- Target: `Churn` (1 = se fue, 0 = sigue). Desbalance: ~16,8% churn.
- 7 columnas con nulos. Diccionario de variables en la hoja `Data Dict` del Excel.
- Original en `data/raw/` — **no se edita**.

## Estructura
- `PLAN.md` — plan de trabajo de las 3 semanas.
- `decisions.md` — registro de decisiones del proyecto.
- `notebooks/` — `00_semana1.ipynb` (entendimiento + hipótesis); más adelante EDA y modelado.
- `reports/` — entendimiento de negocio, hipótesis y (más adelante) reporte ejecutivo.
- `data/raw/` — dataset original (intocable).
- `src/data_prep.py` — carga y limpieza compartida.
- `.claude/skills/` — skills del data-science-kit instaladas (ver abajo).

## Skills instaladas (`.claude/skills/`)
Subagentes del data-science-kit (agus-chaud) que Claude Code usa de forma nativa:

| Skill | Para qué |
|---|---|
| `ds-explorer` | EDA: perfila datos, detecta calidad, genera/valida hipótesis |
| `ds-feature` | Feature engineering (modo ML y modo negocio) |
| `ds-stats` | Estadística e inferencia (tests, intervalos, supuestos) |
| `ds-report` | Traduce hallazgos técnicos a reporte ejecutivo |
| `ds-reviewer` | QA crítico / auditoría del análisis |

(`grill-me` y `gentle-ai` se usan instaladas a nivel global.)

## Cómo correrlo
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

## Entregas (consigna v2)
| Entrega | Fecha |
|---|---|
| EDA + Código/GitHub/Skills | 12/06 |
| Notebook Modelado | 19/06 |
| decisions.md | 12/06 y 19/06 |
| Reporte ejecutivo + Defensa oral | 19/06 |
