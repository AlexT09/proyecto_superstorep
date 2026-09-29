import type { Stats } from "./stats";

export function buildAiContext(s: Stats, source: string) {
  const r = (v: number, d = 2) => +v.toFixed(d);
  const grp = (g: Stats["byCategory"]) =>
    g.slice(0, 15).map((x) => ({
      nivel: x.name,
      pedidos: x.orders,
      ventas_totales: r(x.totalSales),
      venta_media: r(x.meanSales),
      venta_mediana: r(x.medianSales),
      beneficio: r(x.totalProfit),
      margen: r(x.margin, 3),
      descuento_medio: r(x.meanDiscount, 3),
    }));
  return JSON.stringify({
    fuente: source,
    pedidos: s.n,
    ventas_totales: r(s.totalSales),
    beneficio_total: r(s.totalProfit),
    margen: r(s.margin, 3),
    resumen_sales: Object.fromEntries(Object.entries(s.sales).map(([k, v]) => [k, r(v)])),
    resumen_log_sales: Object.fromEntries(Object.entries(s.logSales).map(([k, v]) => [k, r(v, 3)])),
    por_categoria: grp(s.byCategory),
    por_region: grp(s.byRegion),
    por_segmento: grp(s.bySegment),
    eta2_log_sales: {
      category: r(s.eta.category, 4),
      region: r(s.eta.region, 4),
      segment: r(s.eta.segment, 4),
    },
    correlaciones_pearson_con_sales: {
      discount: r(s.corr.discount, 3),
      quantity: r(s.corr.quantity, 3),
      profit: r(s.corr.profit, 3),
    },
    corr_discount_profit: r(s.corr.discountProfit, 3),
    pct_pedidos_con_perdida: r(s.lossOrdersPct, 3),
    pct_perdida_en_descuento_ge_30: r(s.highDiscountLossPct, 3),
  });
}
