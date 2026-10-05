"""
dashboard/build_dashboard.py — Genera el dashboard de ventas como un HTML autocontenido.

Las figuras se construyen en Python con Plotly (estilo, trazas, hover) a partir del dataset
transformado, y se incrustan en dashboard/template.html junto con una versión compacta de los
datos. En el navegador, los filtros (categoría, región, segmento, año) recalculan solo los
arreglos de datos de cada figura; el diseño sigue siendo el que define este script.

Ejecutar:  python dashboard/build_dashboard.py            ->  assets/dashboard.html
           python dashboard/build_dashboard.py --offline  (incrusta plotly.js, sin CDN)
La pestaña "Dashboard" de la app Dash lo muestra en un iframe (/assets/dashboard.html).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as po

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import BRAND, BRAND_DARKER, BRAND_LIGHT, ROOT, TEXT, load_data  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent / "template.html"
OUT = ROOT / "assets" / "dashboard.html"

# Paleta categórica (orden fijo, validada para daltonismo): el azul de marca + dos acentos.
CATS = ["Furniture", "Office Supplies", "Technology"]
CAT_COLORS = {"Furniture": "#2E7FB8", "Office Supplies": "#D9822B", "Technology": "#8A63C7"}
REGIONS = ["Central", "East", "South", "West"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
FACTORS = [("Category", "Categoría"), ("Region", "Región"), ("Segment", "Segmento")]
# Tramos de descuento: (etiqueta, límite inferior exclusivo, límite superior inclusivo)
DISC_BINS = [("Sin descuento", -1, 0.0), ("1–20 %", 0.0, 0.2), ("21–40 %", 0.2, 0.4), ("Más de 40 %", 0.4, 1.0)]
SEQ_SCALE = [[0, BRAND_LIGHT], [0.5, "#63A0BC"], [1, BRAND_DARKER]]
GRID = "#EEF0F6"
MUTED = "#7a7e96"


# ---------------------------------------------------------------- agregados
def eta_squared(df: pd.DataFrame, col: str) -> float:
    """Proporción de la varianza de log(Sales) explicada por los grupos de `col` (η², ANOVA de una vía)."""
    y = np.log(df.Sales)
    if df[col].nunique() < 2:
        return float("nan")
    sst = ((y - y.mean()) ** 2).sum()
    g = y.groupby(df[col])
    ssb = (g.count() * (g.mean() - y.mean()) ** 2).sum()
    return float(ssb / sst) if sst else float("nan")


def disc_bucket(d: pd.Series) -> pd.Series:
    out = pd.Series(index=d.index, dtype=object)
    for label, lo, hi in DISC_BINS:
        out[(d > lo) & (d <= hi)] = label
    return out


def metric(series_by_group, kind):
    return {"mean": series_by_group.mean(), "median": series_by_group.median(), "sum": series_by_group.sum()}[kind]


# ---------------------------------------------------------------- figuras
def base_layout(fig, height=300, margin=None, showlegend=False, **kw):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=margin or dict(l=56, r=16, t=12, b=40),
        font=dict(family="Nunito, Segoe UI, sans-serif", color=TEXT, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        barcornerradius=4, bargap=0.35,
        hoverlabel=dict(bgcolor="white", bordercolor="#D5D8E3", font=dict(color=TEXT, size=12)),
        showlegend=showlegend, **kw,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#D5D8E3", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def fig_eta(df):
    vals = [eta_squared(df, c) * 100 for c, _ in FACTORS]
    fig = go.Figure(go.Bar(
        y=[lbl for _, lbl in FACTORS], x=vals, orientation="h", marker_color=BRAND,
        text=[f"{v:.1f} %" for v in vals], textposition="outside", cliponaxis=False,
        textfont=dict(color=TEXT),
        hovertemplate="<b>%{y}</b><br>Explica el %{x:.1f} % de la varianza de log(Sales)<extra></extra>",
    ))
    base_layout(fig, height=220, margin=dict(l=90, r=56, t=8, b=36))
    fig.update_xaxes(title_text="% de la varianza de log(Sales) explicada (η²)", ticksuffix=" %",
                     rangemode="tozero", title_font=dict(size=11, color=MUTED))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT, size=13))
    return fig


def fig_factor(df, col, order, kind, colored=False):
    g = metric(df.groupby(col).Sales, kind).reindex(order).dropna()
    colors = [CAT_COLORS[c] for c in g.index] if colored else BRAND
    n = df.groupby(col).size().reindex(g.index)
    fig = go.Figure(go.Bar(
        x=list(g.index), y=g.values, marker_color=colors,
        text=[fmt_money(v) for v in g.values], textposition="outside", cliponaxis=False,
        textfont=dict(color=TEXT), customdata=n.values,
        hovertemplate="<b>%{x}</b><br>%{y:$,.2f}<br>%{customdata:,} líneas de pedido<extra></extra>",
    ))
    base_layout(fig, height=260, margin=dict(l=56, r=12, t=24, b=36))
    fig.update_yaxes(tickprefix="$", rangemode="tozero")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_trend(df):
    months = sorted(df.Order_Date.dt.strftime("%Y-%m").unique())
    m = df.assign(mes=df.Order_Date.dt.strftime("%Y-%m")).pivot_table(
        index="mes", columns="Category", values="Sales", aggfunc="sum").reindex(months)
    fig = go.Figure()
    for c in CATS:
        y = m[c].round(2).tolist()
        fig.add_trace(go.Scatter(
            x=months, y=y, name=c, mode="lines", line=dict(color=CAT_COLORS[c], width=2),
            hovertemplate=f"{c}: %{{y:$,.0f}}<extra></extra>",
        ))
    base_layout(fig, height=320, hovermode="x unified", showlegend=True,
                legend=dict(orientation="h", y=1.08, x=0, font=dict(color=TEXT)),
                margin=dict(l=56, r=16, t=30, b=40))
    fig.update_xaxes(type="category", nticks=8, tickangle=0, showgrid=False)
    fig.update_yaxes(tickprefix="$", rangemode="tozero")
    return fig


def fig_box(df):
    fig = go.Figure()
    for c in CATS:
        fig.add_trace(go.Box(
            y=df.loc[df.Category == c, "Sales"].round(2).tolist(), name=c,
            marker_color=CAT_COLORS[c], line=dict(width=1.5), boxpoints=False, boxmean=True,
            fillcolor=hex_alpha(CAT_COLORS[c], 0.18),
            hoverinfo="y",
        ))
    base_layout(fig, height=320, margin=dict(l=64, r=12, t=12, b=40))
    fig.update_yaxes(type="log", dtick=1, title_text="Venta por línea (USD, escala log)", tickprefix="$",
                     title_font=dict(size=11, color=MUTED))
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_heat(df):
    p = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="mean").reindex(
        index=REGIONS, columns=CATS)
    fig = go.Figure(go.Heatmap(
        z=p.round(1).values.tolist(), x=[c for c in CATS], y=REGIONS, colorscale=SEQ_SCALE,
        texttemplate="$%{z:,.0f}", textfont=dict(size=13), xgap=2, ygap=2,
        colorbar=dict(title=dict(text="USD", font=dict(size=11, color=MUTED)), thickness=10,
                      tickfont=dict(color=MUTED), tickprefix="$"),
        hovertemplate="<b>%{y} · %{x}</b><br>Venta media por línea: %{z:$,.2f}<extra></extra>",
    ))
    base_layout(fig, height=300, margin=dict(l=70, r=12, t=12, b=40))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT))
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


def fig_disc(df):
    b = df.assign(tramo=disc_bucket(df.Discount)).groupby("tramo")
    order = [lbl for lbl, _, _ in DISC_BINS]
    mean = b.Sales.mean().reindex(order)
    margin = (b.Profit.sum() / b.Sales.sum() * 100).reindex(order)
    n = b.size().reindex(order)
    fig = go.Figure(go.Bar(
        x=order, y=mean.values, marker_color=BRAND,
        text=[fmt_money(v) for v in mean.values], textposition="outside", cliponaxis=False,
        textfont=dict(color=TEXT), customdata=np.column_stack([margin.values, n.values]),
        hovertemplate=("<b>%{x}</b><br>Venta media por línea: %{y:$,.2f}"
                       "<br>Margen de ganancia: %{customdata[0]:.1f} %<br>%{customdata[1]:,} líneas<extra></extra>"),
    ))
    base_layout(fig, height=300, margin=dict(l=56, r=12, t=24, b=40))
    fig.update_yaxes(tickprefix="$", rangemode="tozero")
    fig.update_xaxes(showgrid=False, tickfont=dict(color=TEXT))
    return fig


# ---------------------------------------------------------------- utilidades
def fmt_money(v):
    if v >= 1e6:
        return f"${v / 1e6:.2f}M"
    if v >= 1e4:
        return f"${v / 1e3:.0f}K"
    return f"${v:,.0f}"


def hex_alpha(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


def compact_data(df):
    """Datos fila a fila en arreglos de índices (pocos KB por columna) para el filtrado en el navegador."""
    months = sorted(df.Order_Date.dt.strftime("%Y-%m").unique())
    subs = sorted(df["Sub-Category"].unique())
    idx = lambda values, col: df[col].map({v: i for i, v in enumerate(values)}).astype(int).tolist()  # noqa: E731
    return {
        "cats": CATS, "regs": REGIONS, "segs": SEGMENTS, "subs": subs, "months": months,
        "subCat": [CATS.index(df.loc[df["Sub-Category"] == s, "Category"].iloc[0]) for s in subs],
        "discBins": DISC_BINS, "catColors": [CAT_COLORS[c] for c in CATS], "brand": BRAND,
        "c": idx(CATS, "Category"), "r": idx(REGIONS, "Region"), "s": idx(SEGMENTS, "Segment"),
        "sc": idx(subs, "Sub-Category"),
        "m": df.Order_Date.dt.strftime("%Y-%m").map({v: i for i, v in enumerate(months)}).tolist(),
        "o": pd.factorize(df["Order ID"])[0].tolist(),
        "sales": df.Sales.round(3).tolist(), "profit": df.Profit.round(3).tolist(),
        "disc": df.Discount.round(2).tolist(),
    }


def build(offline=False) -> Path:
    df = load_data()
    figs = {
        "fig-eta": fig_eta(df),
        "fig-cat": fig_factor(df, "Category", CATS, "mean", colored=True),
        "fig-reg": fig_factor(df, "Region", REGIONS, "mean"),
        "fig-seg": fig_factor(df, "Segment", SEGMENTS, "mean"),
        "fig-trend": fig_trend(df),
        "fig-box": fig_box(df),
        "fig-heat": fig_heat(df),
        "fig-disc": fig_disc(df),
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
    ap.add_argument("--offline", action="store_true", help="incrusta plotly.js en el HTML (~3.5 MB)")
    out = build(ap.parse_args().offline)
    print(f"OK: {out} ({out.stat().st_size / 1024:,.0f} KB)")
