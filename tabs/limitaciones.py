"""tabs/limitaciones.py — Limitaciones del análisis."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Limitaciones", "Qué debe tenerse en cuenta al interpretar los resultados"),
        dbc.Row([
            dbc.Col(soft_card("Datos", html.Ul([
                html.Li("Dataset de ejemplo (2014–2017) de una sola tienda: no generaliza a otros negocios."),
                html.Li("La unidad de análisis es la línea de pedido, no el cliente ni el pedido completo."),
                html.Li("Las ventas muy sesgadas (valores hasta ≈ 22,638 USD) pueden distorsionar medias y correlaciones."),
            ]), "peach"), md=6, className="mb-3"),
            dbc.Col(soft_card("Interpretación", html.Ul([
                html.Li("El análisis es asociativo: no demuestra causalidad."),
                html.Li("La tendencia temporal se apoya en 4 años de datos; no captura efectos externos (economía, competencia)."),
                html.Li("La correlación solo mide relación lineal: el efecto de Discount sobre Sales parece no lineal (ver bins 2D)."),
            ]), "lavender"), md=6, className="mb-3"),
        ]),
    ])
