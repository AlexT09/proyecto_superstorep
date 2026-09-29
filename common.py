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

# ---------------------------------------------------------------- paleta monocromática
# Todo el dashboard usa un único color de marca (azul petróleo); las claves de PASTEL/ACCENT
# ya no representan colores literales, son solo "niveles" (tintas más claras u oscuras del
# mismo azul) para poder distinguir series sin salirse de la paleta de marca.
BRAND = "#2E6F95"
BRAND_DARK = "#1F5570"
BRAND_DARKER = "#153B4E"
BRAND_LIGHT = "#EAF2F7"

PASTEL = {
    "blue": "#DCEBF2",
    "green": "#B7D4E3",
    "peach": "#8FBBD1",
    "pink": "#63A0BC",
    "yellow": "#3B85A8",
    "lavender": "#1F5570",
}
COLORWAY = list(PASTEL.values())
TEXT = "#2f3247"
# Tintas más saturadas, para líneas/puntos que necesitan más contraste sobre blanco
ACCENT = {
    "blue": "#3B85A8",
    "pink": "#63A0BC",
    "green": "#3B85A8",
    "peach": "#1F5570",
    "lavender": "#1F5570",
    "yellow": "#8FBBD1",
}
MARK = BRAND_DARKER  # color de puntos de referencia (p. ej. la media en un boxplot)
# Tres tintas del mismo azul para distinguir categorías sin salir del color de marca
CATEGORY_COLORS = {
    "Furniture": "#8FBBD1",
    "Office Supplies": "#153B4E",
    "Technology": "#3B85A8",
}
CATEGORY_ACCENT = {
    "Furniture": "#63A0BC",
    "Office Supplies": "#153B4E",
    "Technology": "#1F5570",
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
    """Tarjeta blanca con un acento de color sutil (borde) según `color`."""
    classes = f"soft-card accent-{color}" + (" h-100" if height_full else "")
    return dbc.Card(
        [dbc.CardHeader(title, className="soft-card-header"),
         dbc.CardBody(body)],
        className=classes,
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
        className=f"kpi-card accent-{color} h-100",
    )
