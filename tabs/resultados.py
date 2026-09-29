"""tabs/resultados.py — Análisis exploratorio: univariado y bivariado."""
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from common import (ACCENT, CATEGORY_ACCENT, CATEGORY_COLORS, COLORWAY, PASTEL, TEXT,
                    insight, load_data, page_header, soft_card, style_fig)

CFG = {"displayModeBar": False}


def _graph(fig, height=None):
    return dcc.Graph(figure=fig if height is None else style_fig(fig, height), config=CFG)


def _mean_markers(df, col):
    """Punto sobre la media de cada grupo (equivalente a stat_summary de ggplot)."""
    return [go.Scatter(x=[c], y=[y], mode="markers", marker=dict(color=TEXT, size=9, line=dict(width=1, color="white")),
                       showlegend=False) for c, y in df.groupby(col).Sales.mean().items()]


# ------------------------------------------------------------ análisis univariado
def _resumen_tabla(df):
    s = df.Sales
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    filas = [
        ("n", f"{len(s):,}"), ("media", f"{s.mean():.0f}"), ("ds", f"{s.std():.0f}"),
        ("mediana", f"{s.median():.1f}"), ("q1", f"{q1:.1f}"), ("q3", f"{q3:.0f}"),
        ("RIC", f"{q3 - q1:.0f}"), ("minimo", f"{s.min():.1f}"), ("maximo", f"{s.max():.0f}"),
    ]
    return dbc.Table(
        [html.Thead(html.Tr([html.Th(k) for k, _ in filas])), html.Tbody(html.Tr([html.Td(v) for _, v in filas]))],
        hover=True, responsive=True, borderless=True, size="sm",
    )


def _hist_sales(df, color):
    fig = px.histogram(df[df.Sales <= 1000], x="Sales", nbins=40, color_discrete_sequence=[PASTEL[color]])
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(title="Ventas")
    fig.update_yaxes(title="Número de pedidos")
    return style_fig(fig, 320)


def _hist_log(df, color):
    fig = px.histogram(df, x=np.log(df.Sales), nbins=50, histnorm="probability density",
                       color_discrete_sequence=[PASTEL[color]])
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(title="Log(Ventas)")
    fig.update_yaxes(title="Densidad")
    return style_fig(fig, 320)


def _barras(df, col, xlabel, color):
    t = df[col].value_counts().rename_axis(col).reset_index(name="n")
    t["pct"] = t.n / t.n.sum() * 100
    t = t.sort_values("n")
    fig = px.bar(t, x=col, y="n", text=t.apply(lambda r: f"{r.n:,} ({r.pct:.1f}%)", axis=1),
                 color_discrete_sequence=[PASTEL[color]])
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title="Número de pedidos")
    return style_fig(fig, 320)


def _univariado(df):
    return html.Div([
        html.H4("1 · Análisis univariado", className="section-title"),
        dbc.Row([
            dbc.Col(soft_card("Resumen estadístico de Sales", [
                _resumen_tabla(df),
                insight("La media (230) es 4 veces la mediana (54.5) y la desviación estándar (623) supera a "
                        "la media, lo que confirma una fuerte asimetría positiva: la mayoría de los pedidos "
                        "son de bajo valor y unos pocos pedidos muy grandes (hasta 22638) jalan el promedio "
                        "hacia arriba. El RIC de 193 (entre Q1=17.3 y Q3=210) muestra que el 50% central de "
                        "los pedidos se mueve en un rango moderado."),
            ], "blue"), md=12, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Histograma de Sales", [
                _graph(_hist_sales(df, "peach")),
                insight("Confirma visualmente el sesgo a la derecha: la gran mayoría de las barras se "
                        "concentran en valores bajos de venta, con una cola larga y dispersa hacia la "
                        "derecha."),
            ], "peach"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Densidad de log(Sales)", [
                _graph(_hist_log(df, "pink")),
                insight("Al aplicar el logaritmo, la distribución se vuelve más simétrica y manejable. La "
                        "mayor concentración de observaciones se encuentra aproximadamente entre "
                        "log(Sales) = 2.7 y 3.7, donde la densidad alcanza un máximo cercano a 0.24. "
                        "Posteriormente, la densidad disminuye progresivamente a medida que aumentan los "
                        "valores de log(Sales), mostrando una menor concentración de ventas altas."),
            ], "pink"), lg=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Barras: pedidos por categoría", [
                _graph(_barras(df, "Category", "Categoría", "blue")),
                insight("Office Supplies concentra el 60.3% de los pedidos (6026), muy por encima de "
                        "Furniture (21.2%, 2121) y Technology (18.5%, 1847). Es decir, Office Supplies es la "
                        "categoría que más rota en número de pedidos."),
            ], "blue"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Barras: pedidos por región", [
                _graph(_barras(df, "Region", "Región", "green")),
                insight("West tiene mayor numero de pedidos con 3203 pedidos, seguida de East con 2848. "
                        "Central con 2323 y South con menor numero de pedidos con 1620."),
            ], "green"), lg=6, className="mb-3"),
        ]),
    ])


# ------------------------------------------------------------- análisis bivariado
def _box_raw(df, col, xlabel):
    seq = None if col == "Category" else COLORWAY
    cmap = CATEGORY_COLORS if col == "Category" else None
    fig = px.box(df, x=col, y="Sales", color=col, color_discrete_map=cmap, color_discrete_sequence=seq)
    fig.add_traces(_mean_markers(df, col))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title="Ventas")
    return style_fig(fig, 340)


def _box_log(df, col, xlabel):
    d = df.assign(log_sales=np.log(df.Sales))
    seq = None if col == "Category" else COLORWAY
    cmap = CATEGORY_COLORS if col == "Category" else None
    fig = px.box(d, x=col, y="log_sales", color=col, color_discrete_map=cmap, color_discrete_sequence=seq)
    fig.add_traces([go.Scatter(x=[c], y=[y], mode="markers",
                               marker=dict(color=TEXT, size=9, line=dict(width=1, color="white")), showlegend=False)
                    for c, y in d.groupby(col).log_sales.mean().items()])
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title="Log(Ventas)")
    return style_fig(fig, 340)


def _burbuja(df):
    t = df.groupby(["Category", "Region"]).size().reset_index(name="n")
    fig = px.scatter(t, x="Category", y="Region", size="n", color="Category",
                     color_discrete_map=CATEGORY_COLORS, size_max=45)
    fig.update_traces(marker=dict(line=dict(width=1, color="white")))
    fig.update_xaxes(title="Categoría")
    fig.update_yaxes(title="Región")
    return style_fig(fig, 340)


def _bins2d(df):
    fig = px.density_heatmap(df, x="Discount", y="Sales", nbinsx=16, nbinsy=40,
                             color_continuous_scale=[[0, "#FFFFFF"], [0.3, PASTEL["yellow"]], [0.6, PASTEL["peach"]], [1, PASTEL["pink"]]])
    fig.update_yaxes(range=[0, 1500])
    fig.update_layout(coloraxis_colorbar=dict(title="Frecuencia"))
    return style_fig(fig, 340)


def _corr(df):
    c = df[["Sales", "Quantity", "Discount", "Profit"]].corr().round(2)
    fig = px.imshow(c, text_auto=True, zmin=-1, zmax=1,
                    color_continuous_scale=[[0, PASTEL["pink"]], [0.5, "#FFFFFF"], [1, PASTEL["blue"]]])
    fig.update_layout(coloraxis_showscale=False)
    return style_fig(fig, 340)


def _tendencia_mensual(df):
    t = (df.assign(mes=df.Order_Date.dt.to_period("M").dt.to_timestamp())
           .groupby("mes", as_index=False).Sales.sum())
    fig = px.scatter(t, x="mes", y="Sales", color_discrete_sequence=[ACCENT["pink"]])
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="white")))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Ventas")
    return style_fig(fig, 340), t


def _tendencia_loess(t):
    fig = px.scatter(t, x="mes", y="Sales", trendline="lowess", trendline_color_override=ACCENT["peach"],
                     color_discrete_sequence=[ACCENT["blue"]])
    fig.update_traces(selector=dict(mode="markers"), marker=dict(size=8, line=dict(width=1, color="white")))
    fig.update_traces(selector=dict(mode="lines"), line=dict(width=3))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Ventas")
    return style_fig(fig, 340)


def _tendencia_categoria(df):
    t = (df.assign(mes=df.Order_Date.dt.to_period("M").dt.to_timestamp())
           .groupby(["Category", "mes"], as_index=False).Sales.sum())
    fig = px.scatter(t, x="mes", y="Sales", color="Category", trendline="lowess",
                     color_discrete_map=CATEGORY_ACCENT)
    for trace in fig.data:
        if trace.mode == "markers":
            trace.showlegend = False
            trace.marker.update(size=6, opacity=.55)
        else:
            trace.line.update(width=3)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Ventas")
    return style_fig(fig, 340)


def _facetas_region(df):
    t = (df.assign(mes=df.Order_Date.dt.to_period("M").dt.to_timestamp())
           .groupby(["Region", "mes"], as_index=False).Sales.sum())
    fig = px.scatter(t, x="mes", y="Sales", facet_col="Region", facet_col_wrap=2,
                     trendline="lowess", trendline_color_override=ACCENT["peach"],
                     color_discrete_sequence=[ACCENT["blue"]])
    fig.update_traces(selector=dict(mode="markers"), marker=dict(size=6, line=dict(width=1, color="white")))
    fig.update_traces(selector=dict(mode="lines"), line=dict(width=3))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(color=TEXT, size=13)))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Ventas")
    return style_fig(fig, 460)


def _bivariado(df):
    return html.Div([
        html.H4("2 · Análisis bivariado", className="section-title"),
        dbc.Row([
            dbc.Col(soft_card("Boxplot: Sales por categoría", [
                _graph(_box_raw(df, "Category", "Categoría")),
                insight("Technology muestra el rango de ventas más alto, con ventas que llegan hasta cerca "
                        "de $10000. Office Supplies tiene un rango menor pero con mayor concentración de "
                        "pedidos alrededor de $5000. Furniture es la categoría con menor dispersión y "
                        "menores valores de venta entre las tres."),
            ], "lavender"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Boxplot: log(Sales) por categoría", [
                _graph(_box_log(df, "Category", "Categoría")),
                insight(["Furniture (5.205) con la mediana mas alta junto con Technology (5.113). Office "
                         "Supplies queda muy por debajo (3.311), casi 2 puntos log menos que las otras dos.",
                         html.Br(),
                         "Technology (1.886), seguida muy de cerca por Office Supplies (1.916). Furniture es "
                         "la que tiene la caja más ancha/dispersa (2.224)."]),
            ], "blue"), lg=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Boxplot: Sales por región", [
                _graph(_box_raw(df, "Region", "Región")),
                insight("East y Central muestran los rangos de venta más altos (hasta ~5000 y ~4400 "
                        "respectivamente), y South se mantiene en niveles similares. A diferencia de "
                        "Category, las diferencias entre regiones son menos marcadas."),
            ], "peach"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Boxplot: Sales por segmento", [
                _graph(_box_raw(df, "Segment", "Segmento")),
                insight(["Medianas: Consumer 53.72, Corporate 56.54, Home Office 52.44, ningun segmento "
                         "sobresale.", html.Br(),
                         "Medias: Consumer 223.73, Corporate 233.82, Home Office 240.9, aquí Home Office "
                         "tiene la media más alta.", html.Br(),
                         "Consumer tiene 5191 pedidos, casi el triple que Home Office (1783). Consumer "
                         "genera más ventas totales por tener más pedidos."]),
            ], "green"), lg=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Pedidos por categoría y región", [
                _graph(_burbuja(df)),
                insight("Office Supplies tiene los círculos más grandes (mayor frecuencia de pedidos, ~1000) "
                        "especialmente en West y East. Furniture tiene círculos intermedios (~500) en West y "
                        "Central. Technology presenta los círculos más pequeños en todas las regiones, "
                        "coherente con ser la categoría de menor volumen de pedidos."),
            ], "lavender"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Bins 2D: Discount vs. Sales", [
                _graph(_bins2d(df)),
                insight("La mayoría de los pedidos se concentra en descuentos bajos (0.0-0.2), y las celdas "
                        "con montos de venta más altos aparecen dispersas en varios niveles de descuento."),
            ], "yellow"), lg=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Correlación entre variables continuas", [
                _graph(_corr(df)),
                insight("Sales y Profit tienen la correlación más alta del grupo (0.48, positiva moderada): a "
                        "mayor venta, mayor ganancia, como es esperable. Sales y Quantity tienen una "
                        "correlación débil (0.20). Sales y Discount tienen una correlación prácticamente nula "
                        "(-0.03) en términos lineales, lo que contrasta con el patrón que sí se ve en el "
                        "bins2D: la relación entre descuento y ventas no es lineal, por eso la correlación "
                        "(que solo mide relación lineal) casi no la detecta."),
            ], "pink"), md=12, className="mb-3"),
        ]),
    ])


def _tiempo(df):
    fig_mensual, t_mensual = _tendencia_mensual(df)
    return html.Div([
        html.H4("3 · Ventas en el tiempo", className="section-title"),
        dbc.Row([
            dbc.Col(soft_card("Evolución mensual de ventas", [
                _graph(fig_mensual),
                insight("Los puntos se mantienen relativamente parejos mes a mes, sin un mes que se dispare "
                        "notablemente por encima de los demás — no hay un pico estacional extremo visible a "
                        "simple vista en la dispersión cruda."),
            ], "pink"), lg=6, className="mb-3"),
            dbc.Col(soft_card("Tendencia de ventas en el tiempo (loess)", [
                _graph(_tendencia_loess(t_mensual)),
                insight("Usamos la curva loess para visualizar la tendencia general. La línea de tendencia "
                        "muestra una forma ondulada a lo largo del tiempo, con una leve subida hacia 2017, lo "
                        "que sugiere un crecimiento moderado de las ventas totales hacia el final del "
                        "periodo, más que una tendencia lineal constante."),
            ], "blue"), lg=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Tendencia de ventas por categoría", [
                _graph(_tendencia_categoria(df)),
                insight("Technology es la categoría que muestra mayor crecimiento en el tiempo respecto a "
                        "Furniture y Office Supplies, que se mantienen más estables. Esto es coherente con lo "
                        "visto antes: Technology tiene menos pedidos pero de mayor valor, y ese valor por "
                        "pedido parece ir en aumento. Technology presenta picos donde sobresale claramente "
                        "por encima de las otras dos categorías, reforzando que es la que más impulsa el "
                        "crecimiento."),
            ], "lavender"), md=12, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(soft_card("Tendencia de ventas por región (facetas)", [
                _graph(_facetas_region(df)),
                insight("West se tiene mayor estabilidad y niveles de venta ligeramente más altos en "
                        "comparación de las demás a lo largo del tiempo."),
            ], "green"), md=12, className="mb-3"),
        ]),
    ])


def layout():
    df = load_data()
    return html.Div([
        page_header("Resultados", "Análisis univariado y bivariado del EDA"),
        _univariado(df),
        _bivariado(df),
        _tiempo(df),
    ])
