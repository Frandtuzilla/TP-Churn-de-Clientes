"""Funciones compartidas de carga y limpieza del dataset de churn.
Usadas por los notebooks 01_eda y 02_modelado para no duplicar lógica.
"""
import pandas as pd

RAW_PATH = "data/raw/E_Commerce_Dataset.xlsx"

# Mapeos para corregir categorías inconsistentes detectadas en el EDA
CATEGORY_FIXES = {
    "PreferredLoginDevice": {"Phone": "Mobile Phone"},
    "PreferredPaymentMode": {"CC": "Credit Card", "Cash on Delivery": "COD"},
    "PreferedOrderCat": {"Mobile": "Mobile Phone"},
}

CATEGORICAL_COLS = ["PreferredLoginDevice", "PreferredPaymentMode", "Gender",
                    "PreferedOrderCat", "MaritalStatus"]
# CityTier y SatisfactionScore son ordinales: los dejamos numéricos.
NUMERIC_COLS = ["Tenure", "CityTier", "WarehouseToHome", "HourSpendOnApp",
                "NumberOfDeviceRegistered", "SatisfactionScore", "NumberOfAddress",
                "Complain", "OrderAmountHikeFromlastYear", "CouponUsed",
                "OrderCount", "DaySinceLastOrder", "CashbackAmount"]
TARGET = "Churn"
ID_COL = "CustomerID"


def load_raw():
    """Carga el dataset crudo sin modificar."""
    return pd.read_excel(RAW_PATH, sheet_name="E Comm")


def clean_categories(df):
    """Unifica etiquetas duplicadas en variables categóricas."""
    df = df.copy()
    for col, mapping in CATEGORY_FIXES.items():
        df[col] = df[col].replace(mapping)
    return df


def load_clean():
    """Carga + limpieza de categorías. NO imputa (eso va post-split)."""
    return clean_categories(load_raw())
