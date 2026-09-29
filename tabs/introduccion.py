"""tabs/introduccion.py — Presentación del proyecto y la pregunta de investigación."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Introducción", "Análisis exploratorio de datos del dataset Sample Superstore"),
        dbc.Row([
            dbc.Col(soft_card("El problema", [
                html.P("Sample Superstore es un conjunto de datos de muestra de una gran cadena "
                       "minorista —una simulación con fines analíticos— sobre el que se realiza un "
                       "análisis exploratorio de datos (EDA) para ofrecer información que ayude a la "
                       "empresa a aumentar sus beneficios y, al mismo tiempo, minimizar sus pérdidas."),
            ], "blue"), md=7, className="mb-3"),
            dbc.Col(soft_card("Pregunta problema", [
                html.P(["¿Qué factores (categoría, región, segmento) explican el nivel de ventas (",
                        html.Code("Sales"), ")?"], className="fs-5 fw-bold"),
                html.P("Recorre las pestañas para conocer el contexto, los objetivos, la metodología "
                       "y el EDA.", className="text-muted"),
            ], "lavender"), md=5, className="mb-3"),
        ]),
        html.Div("EDA: Alex Teran y David Estrada", className="footer"),
    ])
