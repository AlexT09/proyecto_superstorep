"""
app.py — Dashboard EDA Superstore (Dash + Bootstrap).
Cada pestaña vive en tabs/<nombre>.py y expone una función layout().
Ejecutar:  python app.py   ->   http://127.0.0.1:8050
"""
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html

from tabs import (conclusiones, contexto, introduccion, limitaciones, marco_teorico,
                  metodologia, objetivos, problema, resultados)

# (id, etiqueta, módulo) — el orden define la navegación
TABS = [
    ("introduccion", "Introducción", introduccion),
    ("contexto", "Contexto", contexto),
    ("problema", "Problema", problema),
    ("objetivos", "Objetivos", objetivos),
    ("marco", "Marco teórico", marco_teorico),
    ("metodologia", "Metodología", metodologia),
    ("resultados", "Resultados", resultados),
    ("limitaciones", "Limitaciones", limitaciones),
    ("conclusiones", "Conclusiones", conclusiones),
]
MODULES = {tab_id: mod for tab_id, _, mod in TABS}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True, title="EDA Superstore")
server = app.server

app.layout = html.Div([
    html.Div(dbc.Container([
        html.H1("EDA Superstore"),
        html.P("Factores que explican el nivel de ventas · Análisis exploratorio de datos (EDA) con Dash"),
    ]), className="app-header"),
    dbc.Container([
        dbc.Tabs([dbc.Tab(label=label, tab_id=tab_id) for tab_id, label, _ in TABS],
                 id="main-tabs", active_tab="introduccion", className="mb-4"),
        dcc.Loading(html.Div(id="tab-content"), type="dot", color="#D5C6E8"),
        html.Div("EDA original: Alex Teran y David Estrada", className="footer"),
    ], fluid="xl"),
])


@app.callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
def render_tab(active_tab):
    """Carga el layout() del módulo correspondiente a la pestaña activa."""
    return MODULES[active_tab].layout()


if __name__ == "__main__":
    app.run(debug=True)
