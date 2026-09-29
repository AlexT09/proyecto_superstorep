"""tabs/contexto.py — Impacto empresarial."""
import dash_bootstrap_components as dbc
from dash import html

from common import kpi_card, load_data, page_header, soft_card


def layout():
    df = load_data()
    ventas_cat = df.groupby("Category").Sales.sum().sort_values(ascending=False)
    top = ventas_cat.index[0]
    share_top10 = df.nlargest(int(len(df) * 0.1), "Sales").Sales.sum() / df.Sales.sum()
    return html.Div([
        page_header("Contexto", "Por qué entender las ventas importa para el negocio"),
        dbc.Row([
            dbc.Col(kpi_card("Ganancia total", f"${df.Profit.sum()/1e3:,.0f} K", "green", "suma de Profit"), md=4, className="mb-3"),
            dbc.Col(kpi_card("Categoría líder en ventas", top, "lavender", f"${ventas_cat.iloc[0]/1e3:,.0f} K"), md=4, className="mb-3"),
            dbc.Col(kpi_card("Peso del 10% de pedidos más grandes", f"{share_top10:.0%}", "pink", "de las ventas totales"), md=4, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Impacto empresarial", html.Ul([
                html.Li("Inventario: saber qué categorías generan pedidos grandes permite dimensionar el stock."),
                html.Li("Marketing: dirigir campañas al segmento y región donde el valor por pedido es mayor."),
                html.Li("Precios y descuentos: entender si descontar realmente impulsa el valor de las ventas."),
                html.Li("Logística: coordinar modos de envío con el volumen y valor de los pedidos."),
            ]), "peach"), md=6, className="mb-3"),
            dbc.Col(soft_card("Lo que muestra el EDA", html.Ul([
                html.Li("Office Supplies domina en número de pedidos (≈60%), pero con montos pequeños."),
                html.Li("Technology tiene menos pedidos, pero de mayor valor y con crecimiento en el tiempo."),
                html.Li("Un puñado de pedidos muy grandes concentra una parte desproporcionada de los ingresos."),
                html.Li("Región y segmento muestran diferencias más leves que la categoría."),
            ]), "blue"), md=6, className="mb-3"),
        ]),
    ])
