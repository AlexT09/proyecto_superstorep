"""tabs/dashboard.py — Dashboard interactivo (React) embebido vía iframe.

Vive como proyecto aparte en dash-src/ (tiene su propio servidor porque incluye
un chat con IA que necesita backend). Para verlo aquí hay que tenerlo corriendo
en paralelo: `cd dash-src && npm run dev` (puerto fijo 5173, ver vite.config.ts).
Si no está corriendo, el iframe se ve en blanco.
"""
from dash import html

from common import page_header, soft_card

DASHBOARD_URL = "http://localhost:5173/"


def layout():
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
        ], "lavender", height_full=False),
    ])
