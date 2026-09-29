"""
export_json.py — Exporta el dataset transformado (superstore_transformado.csv) a JSON
para que los frontends React (dash-src) lo consuman, sin backend Python.

No se altera ningún valor: se leen las mismas columnas que usan las pestañas de Dash
(tabs/*.py) y se serializan tal cual, más un bloque `meta` con los mismos agregados
(KPIs) que hoy calculan introduccion.py y contexto.py en tiempo de carga.
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
SRC = BASE / "superstore_transformado.csv"
OUT_DASH_SRC = BASE.parent / "dash-src" / "src" / "data" / "superstore.json"


def main() -> None:
    df = pd.read_csv(SRC, parse_dates=["Order_Date", "Ship Date"])

    # dash-src (Order[]: category/region/segment/sales/quantity/discount/profit,
    # mismos nombres de campo que src/lib/sales-data.ts) — un id secuencial y los
    # mismos valores sin transformar.
    orders = [
        {
            "id": i + 1,
            "category": r.Category,
            "region": r.Region,
            "segment": r.Segment,
            "sales": round(float(r.Sales), 4),
            "quantity": int(r.Quantity),
            "discount": round(float(r.Discount), 4),
            "profit": round(float(r.Profit), 4),
        }
        for i, r in enumerate(df.itertuples(index=False))
    ]
    OUT_DASH_SRC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DASH_SRC.write_text(json.dumps(orders, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(orders):,} filas -> {OUT_DASH_SRC}")


if __name__ == "__main__":
    main()
