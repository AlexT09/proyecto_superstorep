"""
data/generate_data.py
Replica el ETL del EDA en R (01-intro.Rmd) y prepara el dataset del dashboard.

  Extracción    : lee data/raw/Sample - Superstore.csv (codificación latin1)
  Transformación: convierte fechas (mes/día/año), ordena por fecha de pedido
                  (la variable respuesta del modelo es log(Sales), se calcula al entrenar)
  Carga         : escribe data/superstore_transformado.csv

Uso:  python data/generate_data.py
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw" / "Sample - Superstore.csv"
OUT = BASE / "superstore_transformado.csv"


def main() -> None:
    # --- Extracción
    df = pd.read_csv(RAW, encoding="latin1")

    # --- Transformación
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
    df = df.rename(columns={"Order Date": "Order_Date"}).sort_values("Order_Date")

    # --- Carga
    df.to_csv(OUT, index=False)
    print(f"OK: {len(df):,} filas -> {OUT.name}")


if __name__ == "__main__":
    main()
