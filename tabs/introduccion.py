"""tabs/introduccion.py — Explicación del problema."""
import dash_bootstrap_components as dbc
from dash import html

from common import kpi_card, load_data, page_header, soft_card


def layout():
    df = load_data()
    return html.Div([
        page_header("Introducción", "¿Qué factores explican el nivel de ventas en Superstore?"),
        dbc.Row([
            dbc.Col(kpi_card("Pedidos analizados", f"{len(df):,}", "blue", "líneas de pedido"), md=3, className="mb-3"),
            dbc.Col(kpi_card("Periodo", f"{df.Order_Date.dt.year.min()}–{df.Order_Date.dt.year.max()}", "pink", "fechas de pedido"), md=3, className="mb-3"),
            dbc.Col(kpi_card("Ventas totales", f"${df.Sales.sum()/1e6:.2f} M", "green", "suma de Sales"), md=3, className="mb-3"),
            dbc.Col(kpi_card("Venta mediana", f"${df.Sales.median():.1f}", "peach", "media ≈ 4× la mediana"), md=3, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("El problema", [
                html.P("Este es un conjunto de datos de muestra de una gran cadena minorista —una especie de "
                       "simulación— en el que se realiza un análisis exhaustivo de datos para ofrecer información "
                       "clave sobre cómo la empresa puede aumentar sus beneficios y, al mismo tiempo, minimizar "
                       "las pérdidas."),
                html.P("Este dashboard presenta el análisis exploratorio (EDA) del dataset Sample - Superstore."),
            ], "blue"), md=7, className="mb-3"),
            dbc.Col(soft_card("Pregunta problema", [
                html.P(["¿Qué factores (categoría, región, segmento) explican el nivel de ventas (",
                        html.Code("Sales"), ")?"], className="fs-5 fw-bold"),
                html.P("Navega por las pestañas para recorrer el contexto, los objetivos, la metodología "
                       "y los resultados del EDA.", className="text-muted"),
            ], "lavender"), md=5, className="mb-3"),
        ]),
        html.Div("Autores del EDA: Alex Teran y David Estrada", className="footer"),
    ])
