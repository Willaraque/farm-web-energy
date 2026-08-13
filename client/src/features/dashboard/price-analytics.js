const EPSILON = 0.5;

export function analyzePrices(series) {
  const points = (Array.isArray(series) ? series : []).filter((point) => Number.isFinite(Number(point.price))).map((point) => ({ ...point, price: Number(point.price) }));
  if (!points.length) return null;
  const prices = points.map((point) => point.price);
  const current = points.at(-1); const previous = points.at(-2) || current;
  const average = prices.reduce((sum, price) => sum + price, 0) / prices.length;
  const minimum = points.reduce((best, point) => point.price < best.price ? point : best);
  const maximum = points.reduce((best, point) => point.price > best.price ? point : best);
  const absoluteChange = current.price - previous.price;
  const percentageChange = percentChange(previous.price, current.price);
  const periodChange = percentChange(points[0].price, current.price);
  const variance = prices.reduce((sum, price) => sum + (price - average) ** 2, 0) / prices.length;
  const deviation = Math.sqrt(variance);
  const volatilityPercent = average === 0 ? null : Math.abs(deviation / average) * 100;
  const trend = Math.abs(periodChange ?? 0) < EPSILON ? "neutral" : periodChange > 0 ? "positive" : "negative";
  const range = maximum.price - minimum.price;
  const currentVsAverage = percentChange(average, current.price);
  const sorted = [...prices].sort((a, b) => a - b);
  const q1 = percentile(sorted, .25); const q3 = percentile(sorted, .75);
  return { points, current, previous, average, minimum, maximum, absoluteChange, percentageChange, periodChange, trend, range, deviation, volatilityPercent, currentVsAverage, classification: classify(current.price, q1, q3), insights: createInsights({ current, average, minimum, maximum, periodChange, trend, volatilityPercent, currentVsAverage, points }) };
}

export function percentChange(from, to) {
  if (!Number.isFinite(from) || !Number.isFinite(to) || from === 0) return null;
  return ((to - from) / Math.abs(from)) * 100;
}

export function classify(value, q1, q3) {
  if (value <= q1) return "Bajo";
  if (value >= q3) return "Alto";
  return "Medio";
}

function percentile(sorted, ratio) {
  if (sorted.length === 1) return sorted[0];
  const index = (sorted.length - 1) * ratio; const lower = Math.floor(index); const weight = index - lower;
  return sorted[lower] + ((sorted[lower + 1] ?? sorted[lower]) - sorted[lower]) * weight;
}

function createInsights(stats) {
  const insights = [];
  const trendText = stats.trend === "positive" ? "alcista" : stats.trend === "negative" ? "bajista" : "estable";
  insights.push({ kind: stats.trend, title: `Tendencia ${trendText}`, text: stats.periodChange === null ? "No puede calcularse la variación porque el precio inicial es cero." : `El precio varía ${formatSigned(stats.periodChange)} desde el inicio del periodo.` });
  if (stats.currentVsAverage !== null) insights.push({ kind: stats.currentVsAverage > 0 ? "warning" : "positive", title: stats.currentVsAverage > 0 ? "Por encima de la media" : "Por debajo de la media", text: `El precio actual está un ${Math.abs(stats.currentVsAverage).toFixed(1)} % ${stats.currentVsAverage > 0 ? "por encima" : "por debajo"} del promedio.` });
  if (stats.volatilityPercent !== null) insights.push({ kind: stats.volatilityPercent >= 20 ? "warning" : "neutral", title: `${stats.volatilityPercent >= 20 ? "Alta" : stats.volatilityPercent >= 10 ? "Media" : "Baja"} volatilidad`, text: `La desviación representa un ${stats.volatilityPercent.toFixed(1)} % del precio medio.` });
  const futureCheaper = stats.points.slice(-6).find((point) => point.price < stats.current.price);
  const suggestion = futureCheaper ? `Dentro de los últimos datos del periodo existe un precio inferior a las ${formatPointTime(futureCheaper)}.` : `El menor precio del periodo se registra a las ${formatPointTime(stats.minimum)}.`;
  return { items: insights, suggestion: `${suggestion} Los consumos desplazables podrían beneficiarse de ese tramo.` };
}

export function formatPointTime(point) { return Number.isFinite(point?.hour) ? `${String(point.hour).padStart(2, "0")}:00` : String(point?.date ?? "—"); }
export function formatSigned(value) { return value === null ? "—" : `${value >= 0 ? "+" : ""}${value.toFixed(1)} %`; }
