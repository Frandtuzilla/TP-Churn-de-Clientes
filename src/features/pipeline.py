"""Feature engineering pipeline para el TP Churn (modo ML).

Diseño:
- Split estratificado PRIMERO (test_size=0.2, stratify=y, random_state=42).
- Imputación (mediana) y escalado (RobustScaler) fitean SOLO sobre train.
- Encoding OneHot (drop=None) para las 5 categóricas.
- Features derivadas (`tenure_bajo_queja`, `citytier_alto_queja`,
  `Tenure_was_na`) se calculan DESPUÉS de imputar para que la propagación
  de la imputación se refleje correctamente en las banderas.

Uso:
    from src.features.pipeline import (
        build_pipeline, run_pipeline, RANDOM_STATE, TEST_SIZE,
    )

    X_train_df, X_test_df, y_train, y_test, pipe = run_pipeline()
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

# -------------------- Constantes --------------------
ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "E_Commerce_Dataset.xlsx"
PROCESSED_DIR = ROOT / "data" / "processed"

RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET = "Churn"
ID_COL = "CustomerID"

CATEGORY_FIXES = {
    "PreferredLoginDevice": {"Phone": "Mobile Phone"},
    "PreferredPaymentMode": {"CC": "Credit Card", "Cash on Delivery": "COD"},
    "PreferedOrderCat": {"Mobile": "Mobile Phone"},
}

CATEGORICAL_COLS = [
    "PreferredLoginDevice",
    "PreferredPaymentMode",
    "Gender",
    "PreferedOrderCat",
    "MaritalStatus",
]

# Numéricas continuas (a imputar + escalar)
NUMERIC_CONT_COLS = [
    "Tenure", "WarehouseToHome", "HourSpendOnApp", "NumberOfAddress",
    "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount",
    "DaySinceLastOrder", "CashbackAmount",
]

# Numéricas ordinales discretas (a escalar — sin imputar, no tienen nulls)
NUMERIC_ORD_COLS = ["CityTier", "SatisfactionScore", "NumberOfDeviceRegistered"]

# Binarias (no se tocan)
BINARY_COLS = ["Complain"]

NUMERIC_COLS = NUMERIC_CONT_COLS + NUMERIC_ORD_COLS

# Variables que tienen nulos en el raw (de data_quality.md)
COLS_WITH_NULLS = [
    "Tenure", "WarehouseToHome", "HourSpendOnApp",
    "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount",
    "DaySinceLastOrder",
]


# -------------------- Carga + limpieza --------------------
def load_raw() -> pd.DataFrame:
    return pd.read_excel(RAW_PATH, sheet_name="E Comm")


def fix_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica etiquetas duplicadas. Se aplica ANTES del split (no aprende nada)."""
    df = df.copy()
    for col, mapping in CATEGORY_FIXES.items():
        df[col] = df[col].replace(mapping)
    return df


# -------------------- Pipeline numérico/categórico --------------------
def build_preprocessor() -> ColumnTransformer:
    """ColumnTransformer base: imputa, escala numéricas; OHE para categóricas.

    Las features derivadas y la flag Tenure_was_na se agregan FUERA de este
    transformer (ver build_pipeline) porque requieren la versión imputada
    de Tenure y la columna original Complain.
    """
    numeric_cont_tr = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
    ])
    numeric_ord_tr = Pipeline([
        ("scaler", RobustScaler()),
    ])
    categorical_tr = Pipeline([
        ("ohe", OneHotEncoder(
            drop=None,
            handle_unknown="ignore",
            sparse_output=False,
        )),
    ])
    return ColumnTransformer(
        transformers=[
            ("num_cont", numeric_cont_tr, NUMERIC_CONT_COLS),
            ("num_ord", numeric_ord_tr, NUMERIC_ORD_COLS),
            ("cat", categorical_tr, CATEGORICAL_COLS),
            ("binary", "passthrough", BINARY_COLS),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def get_output_columns(preprocessor: ColumnTransformer) -> list[str]:
    """Devuelve la lista ordenada de nombres de columnas a la salida del
    ColumnTransformer (post-OHE). Asume preprocessor ya fiteado.
    """
    return list(preprocessor.get_feature_names_out())


# -------------------- Features derivadas --------------------
def add_derived_features(df_processed: pd.DataFrame, df_imputed_raw: pd.DataFrame) -> pd.DataFrame:
    """Agrega features derivadas usando la versión imputada del raw.

    Parámetros
    ----------
    df_processed : pd.DataFrame
        Salida del ColumnTransformer ya convertida a DataFrame.
    df_imputed_raw : pd.DataFrame
        El raw post-imputación pero PRE-escalado (Tenure, Complain, CityTier
        en sus escalas originales). Necesario porque las flags binarias se
        definen sobre umbrales en escala original.
    """
    df_processed = df_processed.copy()
    tenure = df_imputed_raw["Tenure"]
    complain = df_imputed_raw["Complain"]
    citytier = df_imputed_raw["CityTier"]

    df_processed["tenure_bajo_queja"] = ((tenure <= 3) & (complain == 1)).astype(int).values
    df_processed["citytier_alto_queja"] = ((citytier > 1) & (complain == 1)).astype(int).values
    return df_processed


def add_null_flags(df_processed: pd.DataFrame, df_pre_imputation: pd.DataFrame) -> pd.DataFrame:
    """Agrega Tenure_was_na (solo para Tenure; predictor #1 según handoff)."""
    df_processed = df_processed.copy()
    df_processed["Tenure_was_na"] = df_pre_imputation["Tenure"].isna().astype(int).values
    return df_processed


# -------------------- Función pública: build_pipeline --------------------
def build_pipeline() -> ColumnTransformer:
    """Devuelve el preprocessor SIN fitear. El Modeler puede reutilizarlo
    para reproducir o componerlo con un clasificador en un Pipeline mayor.
    """
    return build_preprocessor()


# -------------------- Orquestación: split + fit + transform --------------------
def run_pipeline(verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ColumnTransformer]:
    """Ejecuta el pipeline completo:

    1. Carga raw, corrige inconsistencias, drop CustomerID.
    2. Split estratificado.
    3. Fitea preprocessor con TRAIN.
    4. Transforma train y test.
    5. Agrega flag Tenure_was_na (sobre pre-imputación) y features derivadas
       (sobre imputado pre-escalado).
    6. Devuelve DataFrames + serie target + preprocessor fiteado.

    El test set NUNCA se usa para fit.
    """
    # 1. Load + clean categorical labels (no aprende nada del dato)
    df = load_raw()
    df = fix_categories(df)

    # 2. Separar X / y + drop ID
    y = df[TARGET].astype(int)
    X = df.drop(columns=[TARGET, ID_COL])

    # 3. Split ANTES de cualquier transformación que aprenda
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE,
    )
    if verbose:
        print(f"Split: train={len(X_train)} (churn {y_train.mean():.3f}) "
              f"· test={len(X_test)} (churn {y_test.mean():.3f})")

    # 4. Fit + transform numérico/categórico
    preprocessor = build_preprocessor()
    arr_train = preprocessor.fit_transform(X_train)
    arr_test = preprocessor.transform(X_test)

    cols = get_output_columns(preprocessor)
    train_df = pd.DataFrame(arr_train, columns=cols, index=X_train.index)
    test_df = pd.DataFrame(arr_test, columns=cols, index=X_test.index)

    # 5a. Flag Tenure_was_na (a partir del PRE-imputación)
    train_df = add_null_flags(train_df, X_train)
    test_df = add_null_flags(test_df, X_test)

    # 5b. Features derivadas
    # Necesitamos Tenure / Complain / CityTier en escala original POST-imputación.
    # Reproducimos la imputación de Tenure usando la mediana fiteada con train.
    tenure_median = (
        preprocessor.named_transformers_["num_cont"]
        .named_steps["imputer"].statistics_[NUMERIC_CONT_COLS.index("Tenure")]
    )
    train_imputed = X_train.copy()
    test_imputed = X_test.copy()
    train_imputed["Tenure"] = train_imputed["Tenure"].fillna(tenure_median)
    test_imputed["Tenure"] = test_imputed["Tenure"].fillna(tenure_median)

    train_df = add_derived_features(train_df, train_imputed)
    test_df = add_derived_features(test_df, test_imputed)

    # 6. Agregar target para guardar (handy para el Modeler)
    train_df[TARGET] = y_train.values
    test_df[TARGET] = y_test.values

    return train_df, test_df, y_train, y_test, preprocessor


def save_processed(train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_parquet(PROCESSED_DIR / "features_train.parquet", index=False)
    test_df.to_parquet(PROCESSED_DIR / "features_test.parquet", index=False)


if __name__ == "__main__":
    train_df, test_df, y_train, y_test, preproc = run_pipeline()
    save_processed(train_df, test_df)
    print(f"Train shape: {train_df.shape} · Test shape: {test_df.shape}")
    print(f"Features de salida: {list(train_df.columns)}")
    print(f"Guardado en: {PROCESSED_DIR}")
