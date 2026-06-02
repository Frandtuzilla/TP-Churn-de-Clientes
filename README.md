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
- `notebooks/` — `01_eda.ipynb` (exploración) y `02_modelado.ipynb` (modelos).
- `reports/` — hipótesis y reporte ejecutivo final.
- `data/raw/` — dataset original.

## Cómo correrlo
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

## Entregas
| Entrega | Fecha |
|---|---|
| EDA + Repo + Skills | 05/06 |
| Notebook Modelado + decisions.md | 12/06 |
| Reporte ejecutivo + Defensa oral | 19/06 |
