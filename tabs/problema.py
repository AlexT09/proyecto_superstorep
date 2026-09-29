"""tabs/problema.py — Nivel de ventas por categoría, región y segmento."""
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from common import PASTEL, insight, load_data, page_header, soft_card, style_fig


def _mediana_fig(df, col, color):
    """Barras con la venta mediana (USD) por grupo."""
    t = df.groupby(col).Sales.median().sort_values().reset_index()
    fig = px.bar(t, x="Sales", y=col, orientation="h", text=t.Sales.map("${:,.1f}".format),
                 color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_xaxes(title="Venta mediana por pedido (USD)", range=[0, t.Sales.max() * 1.25])
    fig.update_yaxes(title=None)
    return style_fig(fig, 280)


def _graph(fig):
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def layout():
    df = load_data()
    return html.Div([
        page_header("Planteamiento del problema",
                    "¿Cambia el nivel de ventas según categoría, región y segmento?"),
        dbc.Row([
            dbc.Col(soft_card("Pregunta problema", html.P(
                ["¿Qué factores (categoría, región, segmento) explican el nivel de ventas (",
                 html.Code("Sales"), ")?"], className="fs-5 fw-bold mb-0"),
                "lavender"), md=12, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Por categoría", _graph(_mediana_fig(df, "Category", PASTEL["lavender"])), "lavender"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Por región", _graph(_mediana_fig(df, "Region", PASTEL["blue"])), "blue"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Por segmento", _graph(_mediana_fig(df, "Segment", PASTEL["green"])), "green"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Lectura", [
                html.P("La categoría marca la mayor diferencia: la venta mediana de Furniture y Technology "
                       "es varias veces la de Office Supplies."),
                html.P("Región y segmento se mueven en rangos mucho más estrechos, en línea con la conclusión del EDA: "
                       "Category es el factor que más explica el nivel de ventas."),
                insight(f"Se usa la mediana porque Sales es muy asimétrica (media ${df.Sales.mean():,.0f} vs. "
                        f"mediana ${df.Sales.median():,.1f})."),
            ], "peach"), lg=6, className="mb-3"),
        ]),
    ])
