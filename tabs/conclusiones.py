"""tabs/conclusiones.py — Conclusión del EDA."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Conclusiones", "Lo que aprendimos del análisis"),
        dbc.Row([
            dbc.Col(soft_card("Conclusión", [
                html.P(["El análisis univariado muestra que ", html.Code("Sales"), " tiene una distribución "
                        "muy sesgada hacia valores bajos, con pocos pedidos de alto valor. El análisis "
                        "bivariado indica que ", html.Code("Category"), " es el factor que más explica "
                        "diferencias en el valor de venta — Technology y Furniture tienen pedidos "
                        "individuales más grandes, mientras que Office Supplies domina en volumen pero con "
                        "pedidos de menor valor."]),
                html.P([html.Code("Region"), " y ", html.Code("Segment"), " muestran diferencias más leves. "
                        "El descuento no se relaciona linealmente con las ventas: en el gráfico de bins 2D "
                        "los descuentos muy altos se asocian con pedidos de menor valor, pero la relación no "
                        "es constante. En el tiempo, las ventas crecen desde 2016 y se concentran hacia el "
                        "final de cada año."], className="mb-0"),
            ], "peach"), md=12, className="mb-3"),
        ]),
    ])
