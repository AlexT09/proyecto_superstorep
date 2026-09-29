"""tabs/marco_teorico.py — Conceptos y tabla de operacionalización de variables."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card

# (variable, definición conceptual, tipo, escala / valores, rol)
VARIABLES = [
    ("Sales", "Valor monetario de la línea de pedido", "Numérica continua", "USD (≥ 0)", "Numérica"),
    ("log(Sales)", "Logaritmo natural de Sales (corrige la asimetría)", "Numérica continua", "Reales", "Transformación para el EDA"),
    ("Category", "Familia de producto", "Categórica nominal", "Furniture, Office Supplies, Technology", "Categórica"),
    ("Sub-Category", "Subcategoría de producto dentro de Category", "Categórica nominal", "17 subcategorías (p. ej. Chairs, Binders, Phones)", "Categórica"),
    ("Region", "Región geográfica del pedido", "Categórica nominal", "Central, East, South, West", "Categórica"),
    ("Segment", "Tipo de cliente", "Categórica nominal", "Consumer, Corporate, Home Office", "Categórica"),
    ("Ship Mode", "Modalidad de envío", "Categórica nominal", "Standard, Second, First Class, Same Day", "Categórica"),
    ("Quantity", "Unidades por línea de pedido", "Numérica discreta", "Enteros (1–14)", "Numérica"),
    ("Discount", "Descuento aplicado", "Numérica continua", "Proporción 0–0.8", "Numérica"),
    ("Profit", "Ganancia de la línea de pedido", "Numérica continua", "USD (puede ser negativa)", "Numérica"),
]


def layout():
    tabla = dbc.Table(
        [html.Thead(html.Tr([html.Th(h) for h in ["Variable", "Definición", "Tipo", "Escala / valores", "Rol"]])),
         html.Tbody([html.Tr([html.Td(html.B(v[0]))] + [html.Td(c) for c in v[1:]]) for v in VARIABLES])],
        hover=True, responsive=True, borderless=True,
    )
    return html.Div([
        page_header("Marco teórico", "Conceptos clave y operacionalización de variables"),
        dbc.Row([
            dbc.Col(soft_card("Análisis exploratorio (EDA)", html.P(
                "Resume y visualiza los datos antes de sacar conclusiones: variación de cada variable "
                "(univariado) y covariación entre variables (bivariado)."), "blue"), md=12, className="mb-3"),
        ]),
        html.H4("Operacionalización de variables", className="section-title"),
        soft_card("Tabla de operacionalización", tabla, "green"),
    ])
