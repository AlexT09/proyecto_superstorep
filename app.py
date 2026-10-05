"""
app.py — Proyecto Sample Superstore (Dash + Bootstrap).
Cada pestaña vive en tabs/<nombre>.py y expone una función layout().
Ejecutar:  python app.py   ->   http://127.0.0.1:8050
"""
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html
from flask import send_from_directory

from common import ROOT
from dashboard.build_dashboard import OUT, build

from tabs import (conclusiones, contexto, dashboard, eda, introduccion, limitaciones,
                  marco_teorico, metodologia, objetivos, problema)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True, title="Proyecto Sample Superstore")
server = app.server

# Dashboard 3D (3DWebDashboard/). Se sirve aparte de assets/ para que Dash no inyecte su
# support.js en la app. Su vista de gráficos lee los datos de assets/dashboard.html.
WEB3D_DIR = ROOT / "3DWebDashboard"


@server.route("/3d/<path:filename>")
def web3d(filename):
    if filename == "dashboard_data.html":
        if not OUT.exists():
            build()
        return send_from_directory(OUT.parent, OUT.name)
    return send_from_directory(WEB3D_DIR, filename)

# (id, etiqueta, módulo) — el orden define la navegación
TABS = [
    ("introduccion", "Introducción", introduccion),
    ("contexto", "Contexto", contexto),
    ("problema", "Problema", problema),
    ("objetivos", "Objetivos", objetivos),
    ("marco", "Marco teórico", marco_teorico),
    ("metodologia", "Metodología", metodologia),
    ("eda", "EDA", eda),
    ("dashboard", "Dashboard", dashboard),
    ("limitaciones", "Limitaciones", limitaciones),
    ("conclusiones", "Conclusiones", conclusiones),
]
MODULES = {tab_id: mod for tab_id, _, mod in TABS}

app.layout = html.Div([
    html.Div(dbc.Container([
        html.H1("Proyecto Sample Superstore"),
        html.P("Factores que explican el nivel de ventas · Análisis exploratorio de datos (EDA) con Dash"),
    ]), className="app-header"),
    dbc.Container([
        dbc.Tabs([dbc.Tab(label=label, tab_id=tab_id) for tab_id, label, _ in TABS],
                 id="main-tabs", active_tab="introduccion", className="mb-4"),
        dcc.Loading(html.Div(id="tab-content"), type="dot", color="#2E6F95"),
        html.Div("Proyecto: Alex Teran y David Estrada", className="footer"),
    ], fluid="xl"),
])


@app.callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
def render_tab(active_tab):
    """Carga el layout() del módulo correspondiente a la pestaña activa."""
    return html.Div(MODULES[active_tab].layout(), className="fade-in")


if __name__ == "__main__":
    app.run(debug=True)
