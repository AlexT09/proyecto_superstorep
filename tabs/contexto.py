"""tabs/contexto.py — Contexto y motivación del análisis."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Contexto", "Por qué entender los factores del nivel de ventas importa para el negocio"),
        dbc.Row([
            dbc.Col(soft_card("Motivación", html.P(
                "Una cadena minorista como Sample Superstore vende a través de múltiples categorías de "
                "producto, regiones y segmentos de cliente. Entender qué combinación de estos factores "
                "está asociada a pedidos de mayor o menor valor es un insumo directo para decisiones de "
                "negocio: dónde enfocar inventario, a quién dirigir campañas comerciales, y cómo evaluar "
                "el efecto real de los descuentos."), "peach"), md=12, className="mb-3"),
            dbc.Col(soft_card("Impacto empresarial", html.Ul([
                html.Li("Inventario: saber qué categorías generan pedidos de mayor valor permite dimensionar el stock."),
                html.Li("Marketing: dirigir campañas al segmento y región donde el valor por pedido es mayor."),
                html.Li("Precios y descuentos: entender si descontar realmente impulsa el valor de las ventas."),
                html.Li("Logística: coordinar modos de envío con el volumen y el valor de los pedidos."),
            ]), "blue"), md=12, className="mb-3"),
        ]),
    ])
