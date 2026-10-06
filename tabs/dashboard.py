"""tabs/dashboard.py — Dashboard 3D de ventas embebido vía iframe.

La portada 3D vive en 3DWebDashboard/3DWebDashboard.html y app.py la sirve en /3d/. Su vista
de gráficos ("Dashboard Superstore.dc.html") toma las figuras y datos de
3DWebDashboard/dashboard_data.json, que genera dashboard/build_dashboard.py (app.py lo genera si
no existe).
"""
from dash import html

from common import page_header, soft_card

DASHBOARD_URL = "/3d/3DWebDashboard.html"


def layout():
    return html.Div([
        page_header("Dashboard", "Dashboard de ventas interactivo — insights que responden a los "
                    "objetivos del proyecto (Sample Superstore)"),
        soft_card("Dashboard 3D de ventas · Sample Superstore", [
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
