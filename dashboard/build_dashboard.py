"""
dashboard/build_dashboard.py — Genera los datos y el HTML del dashboard de ventas.

El dashboard resume el EDA (tabs/eda.py) con el formato de un dashboard ejecutivo: KPIs con
variación anual y, debajo de cada gráfico, el insight del EDA (tabs/eda.py: TEXTOS). Con filtros
activos, dashboard_core.js recalcula una lectura equivalente con los datos filtrados.

Las figuras se definen con Plotly como esqueletos (tipo de traza, ejes, formato). Los datos fila a
fila viajan aparte y 3DWebDashboard/dashboard_core.js llena las figuras según los filtros.

Salidas:
  3DWebDashboard/dashboard_data.json  figuras + datos que lee el dashboard 3D
  assets/dashboard.html               el mismo dashboard en un solo HTML (tema claro)

Ejecutar:  python dashboard/build_dashboard.py            (plotly.js desde CDN)
           python dashboard/build_dashboard.py --offline  (incrusta plotly.js en assets/dashboard.html)
"""
import argparse
import json
import sys
from pathlib import Path

import plotly.graph_objects as go
import plotly.offline as po

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import (BRAND, BRAND_DARK, BRAND_DARKER, BRAND_LIGHT, CATEGORY_COLORS, PASTEL, ROOT,  # noqa: E402
                    STATE_ABBR, TEXT, load_data)
from tabs.eda import TEXTOS  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent / "template.html"
WEB3D_DIR = ROOT / "3DWebDashboard"
CORE_JS = WEB3D_DIR / "dashboard_core.js"
DATA_OUT = WEB3D_DIR / "dashboard_data.json"
OUT = ROOT / "assets" / "dashboard.html"

CATS = ["Furniture", "Office Supplies", "Technology"]
REGIONS = ["Central", "East", "South", "West"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
NUMERIC = ["Sales", "Quantity", "Discount", "Profit"]
HIST_MAX, HIST_BIN = 1000, 25  # mismo recorte del histograma del EDA (Sales <= 1000)
GRID = "#EEF0F6"
MUTED = "#7a7e96"
LEGEND_TOP = dict(orientation="h", x=1, xanchor="right", y=1.02, yanchor="bottom")

# Insight del EDA que acompaña a cada figura del dashboard (sin filtros)
EDA = {
    "fig-hist": TEXTOS["resumen"] + TEXTOS["histograma"],
    "fig-vv-cat": TEXTOS["barras_categoria"],
    "fig-vv-reg": TEXTOS["barras_region"],
    "fig-vv-seg": TEXTOS["box_segmento"][2:],
    "fig-box-cat": TEXTOS["box_categoria"] + TEXTOS["box_log_categoria"],
    "fig-box-reg": TEXTOS["box_region"],
    "fig-box-seg": TEXTOS["box_segmento"][:2],
    "fig-bubble": TEXTOS["burbuja"],
    "fig-bins": TEXTOS["bins2d"],
    "fig-corr": TEXTOS["correlacion"],
    "fig-map": TEXTOS["mapa"],
    "fig-trend": TEXTOS["mensual"],
    "fig-trend-cat": TEXTOS["tendencia_categoria"],
}

# Colores de las trazas en el HTML claro (el dashboard 3D usa su propia paleta oscura)
PAL_LIGHT = {
    "main": BRAND, "soft": "#B7D4E3", "neg": "#B5475A", "ink": TEXT, "accent": BRAND_DARKER, "bg": "#ffffff",
    "boxFill": "rgba(46,111,149,0.08)", "cats": CATEGORY_COLORS,
    "scale": [[0, BRAND_LIGHT], [1, BRAND_DARKER]],
    # escala comprimida: casi todos los pedidos caen en pocas celdas y el resto quedaría invisible
    "seq": [[0, "#FFFFFF"], [0.01, PASTEL["blue"]], [0.15, PASTEL["yellow"]], [1, BRAND_DARKER]],
    "heat": [[0, "#FFFFFF"], [1, BRAND_DARK]],
}


# ---------------------------------------------------------------- figuras (esqueletos)
def base_layout(fig, height=290, margin=None, showlegend=False, **kw):
    fig.update_layout(
        template="plotly_white", height=height, showlegend=showlegend,
        margin=margin or dict(l=56, r=16, t=16, b=40),
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=11.5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", bordercolor="#D5D8E3", font=dict(color=TEXT, size=12)), **kw,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#D5D8E3", tickfont=dict(color=MUTED), fixedrange=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED), fixedrange=True)
    return fig


def fig_hist():
    fig = go.Figure(go.Histogram(x=[], xbins=dict(start=0, end=HIST_MAX, size=HIST_BIN),
                                 hovertemplate="%{x}<br>%{y:,} pedidos<extra></extra>"))
    base_layout(fig, bargap=0.05, margin=dict(l=56, r=16, t=28, b=44))
    fig.update_xaxes(title_text="Ventas (≤ $1,000)", tickprefix="$")
    fig.update_yaxes(title_text="Número de pedidos")
    return fig


def fig_volumen_valor(order):
    fig = go.Figure([
        go.Bar(name="% pedidos", x=order, y=[],
               hovertemplate="<b>%{x}</b><br>%{y:.1f}% de los pedidos (%{customdata})<extra></extra>"),
        go.Bar(name="% ventas", x=order, y=[],
               hovertemplate="<b>%{x}</b><br>%{y:.1f}% de las ventas (%{customdata})<extra></extra>"),
    ])
    base_layout(fig, showlegend=True, barmode="group", bargap=0.3, legend=LEGEND_TOP,
                margin=dict(l=48, r=12, t=36, b=36), hovermode="x unified")
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_box(order):
    fig = go.Figure([go.Box(y=[], name=g, boxpoints=False, boxmean=True, hoverinfo="y") for g in order])
    base_layout(fig, margin=dict(l=64, r=12, t=16, b=36))
    fig.update_yaxes(type="log", dtick=1, tickprefix="$", title_text="Ventas (escala log)")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_burbuja():
    fig = go.Figure([go.Scatter(name=c, x=[], y=[], mode="markers",
                                hovertemplate=f"<b>{c}</b> · %{{y}}<br>%{{customdata:,}} pedidos<extra></extra>")
                     for c in CATS])
    base_layout(fig, height=340, margin=dict(l=72, r=16, t=16, b=40))
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=CATS, title_text="Categoría", showgrid=False)
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=REGIONS, title_text="Región")
    return fig


def fig_bins():
    fig = go.Figure(go.Histogram2d(
        x=[], y=[], xbins=dict(start=0, end=0.85, size=0.05), ybins=dict(start=0, end=1500, size=37.5),
        colorbar=dict(title=dict(text="Frecuencia", font=dict(size=11, color=MUTED)), thickness=10,
                      tickfont=dict(color=MUTED)),
        hovertemplate="Discount %{x}<br>Sales %{y}<br>%{z:,} pedidos<extra></extra>",
    ))
    base_layout(fig, height=340, margin=dict(l=60, r=16, t=16, b=44))
    fig.update_xaxes(title_text="Discount", showgrid=False)
    fig.update_yaxes(title_text="Sales", range=[0, 1500], tickprefix="$", showgrid=False)
    return fig


def fig_corr():
    fig = go.Figure(go.Heatmap(
        z=[], x=NUMERIC, y=NUMERIC, zmin=-1, zmax=1, showscale=False, texttemplate="%{z:.2f}",
        textfont=dict(size=13), xgap=2, ygap=2, hovertemplate="%{y} · %{x}: %{z:.2f}<extra></extra>",
    ))
    base_layout(fig, height=340, margin=dict(l=72, r=12, t=16, b=40))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT))
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_map():
    states = sorted(STATE_ABBR)
    fig = go.Figure(go.Choropleth(
        locations=[STATE_ABBR[s] for s in states], z=[], locationmode="USA-states", marker_line_color="white",
        colorbar=dict(title=dict(text="Pedidos", font=dict(size=11, color=MUTED)), thickness=10, len=0.75,
                      tickfont=dict(color=MUTED)),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>%{z:,} pedidos<extra></extra>",
    ))
    base_layout(fig, height=420, margin=dict(l=0, r=0, t=8, b=0))
    fig.update_layout(geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", showlakes=False))
    return fig


def fig_tendencia():
    fig = go.Figure(go.Scatter(x=[], y=[], mode="lines+markers", hovertemplate="%{x}: %{customdata}<extra></extra>"))
    base_layout(fig, margin=dict(l=56, r=16, t=16, b=40))
    fig.update_xaxes(type="category", nticks=8, tickangle=0, showgrid=False)
    fig.update_yaxes(tickformat="$~s", rangemode="tozero", title_text="Ventas")
    return fig


def fig_tendencia_categoria():
    fig = go.Figure([go.Scatter(name=c, x=[], y=[], mode="lines", hovertemplate=f"{c}: %{{y:$,.0f}}<extra></extra>")
                     for c in CATS])
    base_layout(fig, showlegend=True, legend=LEGEND_TOP, hovermode="x unified", margin=dict(l=56, r=16, t=36, b=40))
    fig.update_xaxes(type="category", nticks=8, tickangle=0, showgrid=False)
    fig.update_yaxes(tickformat="$~s", rangemode="tozero", title_text="Ventas")
    return fig


# ---------------------------------------------------------------- datos
def atipicos_iqr(s):
    """Cuenta valores fuera de [Q1 - 1.5·IQR, Q3 + 1.5·IQR]."""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return int(((s < q1 - 1.5 * (q3 - q1)) | (s > q3 + 1.5 * (q3 - q1))).sum())


def resumen_portada(df):
    """Cifras de las tarjetas del anillo 3D: {título: [valor, detalle]} (pedidos = filas, como en el EDA)."""
    out = {}
    for col in ["Category", "Region", "Segment"]:
        g = df.groupby(col).Sales.agg(["sum", "size"])
        out.update({k: [f"${s:,.0f}", f"{n:,} pedidos"] for k, s, n in zip(g.index, g["sum"], g["size"])})
    out["Pedidos"] = [f"{len(df):,}", "registros totales"]
    out["Media"] = [f"${df.Sales.mean():,.1f}", "por pedido"]
    out["Mediana"] = [f"${df.Sales.median():,.1f}", "por pedido"]
    out["Máximo"] = [f"${df.Sales.max():,.1f}", "pedido más alto"]
    return out


def compact_data(df):
    """Datos fila a fila (categorías como índices) para que los filtros del navegador recalculen todo."""
    months = sorted(df.Order_Date.dt.strftime("%Y-%m").unique())
    states = sorted(STATE_ABBR)
    idx = lambda values, s: s.map({v: i for i, v in enumerate(values)}).astype(int).tolist()  # noqa: E731
    region_of = df.groupby("State").Region.first()
    return {
        "cats": CATS, "regs": REGIONS, "segs": SEGMENTS, "months": months, "numeric": NUMERIC,
        "states": states, "stateRegion": [region_of.get(s, "") for s in states],
        "c": idx(CATS, df.Category), "r": idx(REGIONS, df.Region), "s": idx(SEGMENTS, df.Segment),
        "m": idx(months, df.Order_Date.dt.strftime("%Y-%m")), "st": idx(states, df.State),
        "Sales": df.Sales.round(3).tolist(), "Quantity": df.Quantity.tolist(),
        "Discount": df.Discount.round(2).tolist(), "Profit": df.Profit.round(3).tolist(),
        "histMax": HIST_MAX,
        "eda": EDA,
        "quality": {"filas": len(df), "faltantes": int(df.isna().sum().sum()), "duplicados": int(df.duplicated().sum()),
                    "atipicos_sales": atipicos_iqr(df.Sales), "atipicos_profit": atipicos_iqr(df.Profit)},
        "summary": {"pedidos": f"{len(df):,}", "anios": int(df.Order_Date.dt.year.nunique()),
                    "periodo": f"{df.Order_Date.dt.year.min()}–{df.Order_Date.dt.year.max()}"},
        "ring": resumen_portada(df),
    }


def build(offline=False) -> Path:
    df = load_data()
    data = compact_data(df)
    figs = {
        "fig-hist": fig_hist(),
        "fig-vv-cat": fig_volumen_valor(CATS),
        "fig-vv-reg": fig_volumen_valor(REGIONS),
        "fig-vv-seg": fig_volumen_valor(SEGMENTS),
        "fig-box-cat": fig_box(CATS),
        "fig-box-reg": fig_box(REGIONS),
        "fig-box-seg": fig_box(SEGMENTS),
        "fig-bubble": fig_burbuja(),
        "fig-bins": fig_bins(),
        "fig-corr": fig_corr(),
        "fig-map": fig_map(),
        "fig-trend": fig_tendencia(),
        "fig-trend-cat": fig_tendencia_categoria(),
    }
    figs_json = "{" + ",".join(f'"{k}":{f.to_json()}' for k, f in figs.items()) + "}"
    data_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    # 1) datos del dashboard 3D
    DATA_OUT.write_text(f'{{"figs":{figs_json},"data":{data_json}}}', encoding="utf-8")

    # 2) HTML autocontenido
    plotly_tag = (f"<script>{po.get_plotlyjs()}</script>" if offline else
                  f'<script src="https://cdn.plot.ly/plotly-{po.get_plotlyjs_version()}.min.js"></script>')
    years = sorted(df.Order_Date.dt.year.unique())
    html = (TEMPLATE.read_text(encoding="utf-8")
            .replace("__PLOTLY__", plotly_tag)
            .replace("__CORE__", CORE_JS.read_text(encoding="utf-8"))
            .replace("__PAL__", json.dumps(PAL_LIGHT))
            .replace("__FIGS__", figs_json.replace("</", "<\\/"))
            .replace("__DATA__", data_json.replace("</", "<\\/"))
            .replace("__SUBTITULO__", f'{data["summary"]["periodo"]} · {data["summary"]["pedidos"]} pedidos · Estados Unidos')
            .replace("__YEARS__", "".join(f'<option value="{y}">{y}</option>' for y in years)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="incrusta plotly.js en assets/dashboard.html (~4 MB)")
    out = build(ap.parse_args().offline)
    print(f"OK: {out} ({out.stat().st_size / 1024:,.0f} KB) y {DATA_OUT} ({DATA_OUT.stat().st_size / 1024:,.0f} KB)")
