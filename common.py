"""
common.py
Utilidades compartidas: rutas, carga de datos, paleta pastel y helpers de UI.
Las pestañas (tabs/*.py) solo dependen de este módulo, nunca entre sí.
"""
from functools import lru_cache
from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html

# ---------------------------------------------------------------- rutas
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "superstore_transformado.csv"
MODEL_PATH = ROOT / "model" / "model.pkl"
METRICS_PATH = ROOT / "model" / "metrics.json"

# ---------------------------------------------------------------- paleta pastel
PASTEL = {
    "blue": "#A8D5E5",
    "pink": "#F7C6D0",
    "green": "#C9E4C5",
    "peach": "#FDE2B3",
    "lavender": "#D5C6E8",
    "yellow": "#FFF3B0",
}
COLORWAY = list(PASTEL.values())
TEXT = "#4A4E69"
# Versión más saturada de cada pastel, para líneas/puntos que necesitan más contraste
ACCENT = {
    "blue": "#5B9BC4",
    "pink": "#DB8AA0",
    "green": "#6FAE6F",
    "peach": "#E8A15C",
    "lavender": "#8E7CC3",
    "yellow": "#D9BE3F",
}
# Color fijo por categoría para que todos los gráficos sean coherentes
CATEGORY_COLORS = {
    "Furniture": PASTEL["peach"],
    "Office Supplies": PASTEL["blue"],
    "Technology": PASTEL["lavender"],
}
CATEGORY_ACCENT = {
    "Furniture": ACCENT["peach"],
    "Office Supplies": ACCENT["blue"],
    "Technology": ACCENT["lavender"],
}


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Carga el dataset transformado (salida de data/generate_data.py)."""
    return pd.read_csv(DATA_PATH, parse_dates=["Order_Date", "Ship Date"])


def style_fig(fig, height=360, title=None):
    """Aplica el estilo pastel común a cualquier figura de Plotly."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        title=dict(text=title, font=dict(size=15, color=TEXT)) if title else None,
        font=dict(family="Nunito, Segoe UI, sans-serif", color=TEXT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORWAY,
        margin=dict(l=40, r=20, t=50 if title else 20, b=40),
        legend=dict(orientation="h", y=-0.2),
    )
    fig.update_xaxes(gridcolor="#EEF0F6", zeroline=False)
    fig.update_yaxes(gridcolor="#EEF0F6", zeroline=False)
    return fig


# ---------------------------------------------------------------- helpers de UI
def page_header(title: str, subtitle: str = "", icon: str = "") -> html.Div:
    return html.Div(
        [html.H2(f"{icon} {title}".strip(), className="page-title"),
         html.P(subtitle, className="page-subtitle")],
        className="mb-4",
    )


def soft_card(title, body, color="blue", height_full=True):
    """Tarjeta con encabezado de color pastel."""
    return dbc.Card(
        [dbc.CardHeader(title, style={"backgroundColor": PASTEL[color]}, className="soft-card-header"),
         dbc.CardBody(body)],
        className="soft-card h-100" if height_full else "soft-card",
    )


def insight(children):
    """Párrafo pequeño y discreto para interpretar un gráfico o dato (estilo uniforme en todo el dashboard)."""
    return html.P(children, className="insight-text")


def kpi_card(label, value, color="blue", hint=""):
    return dbc.Card(
        dbc.CardBody([
            html.Div(label, className="kpi-label"),
            html.Div(value, className="kpi-value"),
            html.Div(hint, className="kpi-hint"),
        ]),
        style={"backgroundColor": PASTEL[color]},
        className="kpi-card h-100",
    )
