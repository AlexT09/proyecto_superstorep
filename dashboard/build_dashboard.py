"""
dashboard/build_dashboard.py — Genera el dashboard de ventas como un HTML autocontenido.

Resume en una sola vista los resultados del EDA (tabs/eda.py) según los objetivos del proyecto:
distribución de Sales, pedidos por Category/Region/Segment y por estado (mapa), Sales según cada factor, correlación
entre variables numéricas y tendencia mensual. Las figuras se construyen con Plotly y se incrustan
en dashboard/template.html; los filtros del navegador solo cambian los datos de cada figura.

Ejecutar:  python dashboard/build_dashboard.py            ->  assets/dashboard.html
           python dashboard/build_dashboard.py --offline  (incrusta plotly.js, sin CDN)
"""
import argparse
import json
import sys
from pathlib import Path

import plotly.graph_objects as go
import plotly.offline as po

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import (BRAND, BRAND_DARK, BRAND_DARKER, BRAND_LIGHT, CATEGORY_COLORS, ROOT, STATE_ABBR,  # noqa: E402
                    TEXT, load_data)

TEMPLATE = Path(__file__).resolve().parent / "template.html"
OUT = ROOT / "assets" / "dashboard.html"

CATS = ["Furniture", "Office Supplies", "Technology"]
REGIONS = ["Central", "East", "South", "West"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
NUMERIC = ["Sales", "Quantity", "Discount", "Profit"]
HIST_MAX, HIST_BIN = 1000, 25  # mismo recorte del histograma del EDA (Sales <= 1000)
GRID = "#EEF0F6"
MUTED = "#7a7e96"


# ---------------------------------------------------------------- figuras
def base_layout(fig, height=280, margin=None, showlegend=False, **kw):
    fig.update_layout(
        template="plotly_white", height=height, showlegend=showlegend,
        margin=margin or dict(l=56, r=16, t=16, b=40),
        font=dict(family="Nunito, Segoe UI, sans-serif", color=TEXT, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", bordercolor="#D5D8E3", font=dict(color=TEXT, size=12)), **kw,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#D5D8E3", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def fig_hist(df):
    fig = go.Figure(go.Histogram(
        x=df.loc[df.Sales <= HIST_MAX, "Sales"].round(2).tolist(), marker_color=BRAND,
        xbins=dict(start=0, end=HIST_MAX, size=HIST_BIN),
        hovertemplate="%{x}<br>%{y:,} pedidos<extra></extra>",
    ))
    base_layout(fig, height=300, bargap=0.05)
    fig.update_xaxes(title_text="Ventas (≤ $1,000)", tickprefix="$")
    fig.update_yaxes(title_text="Número de pedidos")
    return fig


def fig_count(df, col, order, colored=False):
    n = df[col].value_counts().reindex(order)
    pct = n / n.sum() * 100
    fig = go.Figure(go.Bar(
        x=order, y=n.values, marker_color=[CATEGORY_COLORS[c] for c in order] if colored else BRAND,
        text=[f"{v:,} ({p:.1f}%)" for v, p in zip(n.values, pct.values)], textposition="outside",
        cliponaxis=False, constraintext="none", textfont=dict(color=TEXT, size=11),
        hovertemplate="<b>%{x}</b><br>%{y:,} pedidos<extra></extra>",
    ))
    base_layout(fig, margin=dict(l=56, r=12, t=24, b=36), bargap=0.25)
    fig.update_yaxes(title_text="Número de pedidos", rangemode="tozero")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_box(df, col, order, colored=False):
    fig = go.Figure()
    for g in order:
        color = CATEGORY_COLORS[g] if colored else BRAND
        fig.add_trace(go.Box(
            y=df.loc[df[col] == g, "Sales"].round(2).tolist(), name=g, marker_color=color,
            line=dict(width=1.5), boxpoints=False, boxmean=True, hoverinfo="y",
        ))
    base_layout(fig, margin=dict(l=64, r=12, t=16, b=36))
    fig.update_yaxes(type="log", dtick=1, tickprefix="$", title_text="Ventas (escala log)")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_map(df):
    t = df.groupby("State").agg(n=("Sales", "size"), region=("Region", "first")).reindex(sorted(STATE_ABBR))
    fig = go.Figure(go.Choropleth(
        locations=[STATE_ABBR[s] for s in t.index], z=t.n.tolist(), locationmode="USA-states",
        colorscale=[[0, BRAND_LIGHT], [1, BRAND_DARKER]], marker_line_color="white",
        colorbar=dict(title=dict(text="Pedidos", font=dict(size=11, color=MUTED)), thickness=10,
                      tickfont=dict(color=MUTED)),
        customdata=list(zip(t.index, t.region)),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>%{z:,} pedidos<extra></extra>",
    ))
    base_layout(fig, height=380, margin=dict(l=0, r=0, t=8, b=0))
    fig.update_layout(geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"))
    return fig


def fig_corr(df):
    c = df[NUMERIC].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=c.values.tolist(), x=NUMERIC, y=NUMERIC, zmin=-1, zmax=1, showscale=False,
        colorscale=[[0, "#FFFFFF"], [1, BRAND_DARK]], texttemplate="%{z:.2f}", textfont=dict(size=13),
        xgap=2, ygap=2, hovertemplate="%{y} · %{x}: %{z:.2f}<extra></extra>",
    ))
    base_layout(fig, height=300, margin=dict(l=72, r=12, t=16, b=40))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT))
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_trend(df):
    mes = df.Order_Date.dt.strftime("%Y-%m")
    m = df.assign(mes=mes).pivot_table(index="mes", columns="Category", values="Sales", aggfunc="sum")
    fig = go.Figure([go.Scatter(
        x=m.index.tolist(), y=m[c].round(2).tolist(), name=c, mode="lines",
        line=dict(color=CATEGORY_COLORS[c], width=2), hovertemplate=f"{c}: %{{y:$,.0f}}<extra></extra>",
    ) for c in CATS])
    base_layout(fig, height=300, hovermode="x unified", showlegend=True,
                legend=dict(orientation="h", y=1.1, x=0, font=dict(color=TEXT)),
                margin=dict(l=64, r=16, t=30, b=40))
    fig.update_xaxes(type="category", nticks=8, tickangle=0, showgrid=False)
    fig.update_yaxes(tickprefix="$", rangemode="tozero", title_text="Ventas")
    return fig


# ---------------------------------------------------------------- datos para los filtros
def compact_data(df):
    """Datos fila a fila (categorías como índices) para que los filtros del navegador recalculen las figuras."""
    months = sorted(df.Order_Date.dt.strftime("%Y-%m").unique())
    idx = lambda values, s: s.map({v: i for i, v in enumerate(values)}).astype(int).tolist()  # noqa: E731
    return {
        "cats": CATS, "regs": REGIONS, "segs": SEGMENTS, "months": months, "numeric": NUMERIC,
        "c": idx(CATS, df.Category), "r": idx(REGIONS, df.Region), "s": idx(SEGMENTS, df.Segment),
        "m": idx(months, df.Order_Date.dt.strftime("%Y-%m")), "st": idx(sorted(STATE_ABBR), df.State),
        "nStates": len(STATE_ABBR),
        "Sales": df.Sales.round(3).tolist(), "Quantity": df.Quantity.tolist(),
        "Discount": df.Discount.round(2).tolist(), "Profit": df.Profit.round(3).tolist(),
        "histMax": HIST_MAX,
    }


def build(offline=False) -> Path:
    df = load_data()
    figs = {
        "fig-hist": fig_hist(df),
        "fig-n-cat": fig_count(df, "Category", CATS, colored=True),
        "fig-n-reg": fig_count(df, "Region", REGIONS),
        "fig-n-seg": fig_count(df, "Segment", SEGMENTS),
        "fig-map": fig_map(df),
        "fig-box-cat": fig_box(df, "Category", CATS, colored=True),
        "fig-box-reg": fig_box(df, "Region", REGIONS),
        "fig-box-seg": fig_box(df, "Segment", SEGMENTS),
        "fig-corr": fig_corr(df),
        "fig-trend": fig_trend(df),
    }
    figs_json = "{" + ",".join(f'"{k}":{f.to_json()}' for k, f in figs.items()) + "}"
    plotly_tag = (f"<script>{po.get_plotlyjs()}</script>" if offline else
                  f'<script src="https://cdn.plot.ly/plotly-{po.get_plotlyjs_version()}.min.js"></script>')
    years = sorted(df.Order_Date.dt.year.unique())
    html = (TEMPLATE.read_text(encoding="utf-8")
            .replace("__PLOTLY__", plotly_tag)
            .replace("__FIGS__", figs_json.replace("</", "<\\/"))
            .replace("__DATA__", json.dumps(compact_data(df), separators=(",", ":")))
            .replace("__PERIODO__", f"{df.Order_Date.min():%d/%m/%Y} – {df.Order_Date.max():%d/%m/%Y}")
            .replace("__YEARS__", "".join(f'<option value="{y}">{y}</option>' for y in years)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="incrusta plotly.js en el HTML (~4 MB)")
    out = build(ap.parse_args().offline)
    print(f"OK: {out} ({out.stat().st_size / 1024:,.0f} KB)")
