"""tabs/objetivos.py — Objetivo general, objetivos específicos y preguntas amplias."""
import dash_bootstrap_components as dbc
from dash import html

from common import page_header, soft_card


def layout():
    return html.Div([
        page_header("Objetivos", "Qué queremos lograr con el EDA"),
        dbc.Row([
            dbc.Col(soft_card("Objetivo general", html.P(
                ["Determinar qué factores (categoría, región y segmento) explican el nivel de ventas (",
                 html.Code("Sales"), ")."], className="fs-5 mb-0"), "pink"), md=12, className="mb-3"),
            dbc.Col(soft_card("Objetivos específicos", html.Ul([
                html.Li(["Describir la distribución de la variable ", html.Code("Sales"), " mediante estadísticos "
                         "de resumen y gráficas univariadas (histograma, densidad de log(Sales))."]),
                html.Li(["Analizar la distribución de los pedidos según las variables categóricas ",
                         html.Code("Category"), ", ", html.Code("Region"), " y ", html.Code("Segment"), "."]),
                html.Li(["Explorar la relación entre ", html.Code("Sales"), " y las variables numéricas ",
                         html.Code("Discount"), ", ", html.Code("Quantity"), " y ", html.Code("Profit"), "."]),
                html.Li(["Evaluar cómo varía ", html.Code("Sales"), " en función de ", html.Code("Category"), ", ",
                         html.Code("Region"), " y ", html.Code("Segment"), "."]),
            ]), "blue"), md=12, className="mb-3"),
            dbc.Col(soft_card("Variables disponibles y su tipo", [
                html.P([html.B("Categóricas: "), html.Code("Category"), ", ", html.Code("Sub-Category"), ", ",
                        html.Code("Region"), ", ", html.Code("Segment"), ", ", html.Code("Ship Mode")]),
                html.P([html.B("Numéricas: "), html.Code("Sales"), ", ", html.Code("Quantity"), ", ",
                        html.Code("Discount"), ", ", html.Code("Profit")]),
            ], "peach"), md=6, className="mb-3"),
            dbc.Col(soft_card("Preguntas amplias", html.Ol([
                html.Li(["Variación (categóricas): ¿Cómo se distribuyen los pedidos entre ", html.Code("Category"),
                         ", ", html.Code("Region"), " y ", html.Code("Segment"), "? ¿Hay categorías con muchos más "
                         "pedidos que otras?"]),
                html.Li(["Variación (numérica): ¿Cómo se distribuye ", html.Code("Sales"), "? ¿La mayoría de los "
                         "pedidos son de bajo valor o hay muchos pedidos grandes?"]),
                html.Li(["Covariación (categórica → numérica): ¿El valor de venta (", html.Code("Sales"),
                         ") cambia según ", html.Code("Category"), ", ", html.Code("Region"), " o ",
                         html.Code("Segment"), "?"]),
                html.Li(["Covariación (numérica → numérica): ¿Existe relación entre ", html.Code("Sales"), " y ",
                         html.Code("Discount"), ", ", html.Code("Quantity"), " o ", html.Code("Profit"), "?"]),
            ]), "green"), md=6, className="mb-3"),
        ]),
    ])
