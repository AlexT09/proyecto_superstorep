"""tabs/dashboard.py — Dashboard de ventas (HTML generado con Python + Plotly) embebido vía iframe.

El HTML lo genera dashboard/build_dashboard.py en assets/dashboard.html, y Dash lo sirve
como archivo estático. Si no existe (p. ej. tras borrarlo), se genera al cargar la pestaña.
"""
from dash import html

from common import page_header, soft_card
from dashboard.build_dashboard import OUT, build

DASHBOARD_URL = "/assets/dashboard.html"


def layout():
    if not OUT.exists():
        build()
    return html.Div([
        page_header("Dashboard", "Dashboard de ventas interactivo — insights que responden a los "
                    "objetivos del proyecto (Sample Superstore)"),
        soft_card("Dashboard de ventas · Sample Superstore", [
            html.Iframe(
                src=DASHBOARD_URL,
                style={
                    "width": "100%",
                    "height": "85vh",
                    "border": "none",
                    "borderRadius": "10px",
                },
            ),
            html.A("Abrir en una pestaña nueva ↗", href=DASHBOARD_URL, target="_blank",
                   className="small d-inline-block mt-2"),
        ], "lavender", height_full=False),
    ])
