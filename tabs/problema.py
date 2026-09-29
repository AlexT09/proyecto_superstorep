"""tabs/problema.py — Planteamiento del problema."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Planteamiento del problema",
                    "Qué buscamos explicar y por qué estas variables"),
        dbc.Row([
            dbc.Col(soft_card("Pregunta problema", html.P(
                ["¿Qué factores (categoría, región, segmento) explican el nivel de ventas (",
                 html.Code("Sales"), ")?"], className="fs-5 fw-bold mb-0"),
                "lavender"), md=12, className="mb-3"),
            dbc.Col(soft_card("Por qué categoría, región y segmento", html.P(
                "Category, Region y Segment son las tres variables categóricas de negocio disponibles "
                "en el dataset que agrupan los pedidos desde ángulos distintos y complementarios: qué "
                "se vende, dónde se vende y a qué tipo de cliente se le vende. El planteamiento del "
                "problema consiste en determinar si el nivel de venta (Sales) cambia de forma relevante "
                "según cada una de ellas; esa evaluación se desarrolla en la sección de EDA."
            ), "blue"), md=12, className="mb-3"),
        ]),
    ])
