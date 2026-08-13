import { useCallback, useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { Activity, ArrowDown, ArrowUp, Gauge, Lightbulb, RefreshCw, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { fetchMarketData } from "../../api/market";
import { getApiError } from "../../api/client";
import { createMarketSeries } from "../market/market-data";
import { analyzePrices, formatPointTime, formatSigned } from "./price-analytics";
import AppLayout from "../../layouts/AppLayout";
import EnergyChart from "./EnergyChart";
import PageHeader from "../../components/PageHeader";
import SpinnerLoader from "../../components/SpinnerLoader";
import StatePanel from "../../components/StatePanel";

const today = () => new Date().toISOString().slice(0, 10);

export default function DashboardPage() {
  const [filters, setFilters] = useState({ desde: today(), hasta: today(), tipo: "Precios-OMIE", mercados: ["diario"] });
  const [series, setSeries] = useState([]); const [status, setStatus] = useState("loading"); const [error, setError] = useState("");
  const load = useCallback(async () => { setStatus("loading"); setError(""); try { const { data } = await fetchMarketData(filters); const next = createMarketSeries(data, "diario"); setSeries(next); setStatus(next.length ? "success" : "empty"); } catch (requestError) { setSeries([]); setError(getApiError(requestError, "No se pudieron cargar los precios.")); setStatus("error"); } }, [filters]);
  useEffect(() => { load(); }, [load]);
  const stats = useMemo(() => analyzePrices(series), [series]);
  const TrendIcon = stats?.trend === "positive" ? TrendingUp : stats?.trend === "negative" ? TrendingDown : Minus;

  return <AppLayout>
    <PageHeader eyebrow="Visión general" title="Panel de energía" description="Evolución, contexto y señales del mercado diario." actions={<button className="button button-secondary" type="button" onClick={load} disabled={status === "loading"}><RefreshCw className={status === "loading" ? "is-spinning" : ""} size={16} />Actualizar</button>} />
    <div className="filter-card dashboard-filters"><label className="field compact">Desde<input type="date" value={filters.desde} max={filters.hasta} onChange={(event) => setFilters((current) => ({ ...current, desde: event.target.value }))} /></label><label className="field compact">Hasta<input type="date" value={filters.hasta} min={filters.desde} onChange={(event) => setFilters((current) => ({ ...current, hasta: event.target.value }))} /></label>{stats && <div className={`trend-summary ${stats.trend}`}><TrendIcon /><span><small>Tendencia</small><strong>{trendLabel(stats.trend)} · {formatSigned(stats.periodChange)}</strong></span></div>}</div>
    <div className="metric-grid analytics-metrics">
      <Metric icon={Activity} label="Precio actual" value={stats?.current.price} tone={stats?.trend} detail={formatSigned(stats?.percentageChange ?? null)} loading={status === "loading"} />
      <Metric icon={Gauge} label="Precio medio" value={stats?.average} detail={stats ? `${stats.classification} en el periodo` : ""} loading={status === "loading"} />
      <Metric icon={ArrowDown} label="Mínimo" value={stats?.minimum.price} tone="positive" detail={stats ? formatPointTime(stats.minimum) : ""} loading={status === "loading"} />
      <Metric icon={ArrowUp} label="Máximo" value={stats?.maximum.price} tone="negative" detail={stats ? formatPointTime(stats.maximum) : ""} loading={status === "loading"} />
    </div>
    <section className={`chart-card market-chart ${stats?.trend || "neutral"}`}><div className="section-heading"><div><h2>Evolución del precio</h2><p>Segmentos verdes indican subida y magenta indica bajada.</p></div>{stats && <span className={`price-level ${stats.classification.toLowerCase()}`}>{stats.classification}</span>}</div><div className="chart-area">{status === "loading" && <SpinnerLoader label="Cargando mercado" />}{status === "error" && <StatePanel type="error" title="No se pudieron cargar los datos" description={error} action={<button className="button button-secondary" type="button" onClick={load}>Reintentar</button>} />}{status === "empty" && <StatePanel title="No hay datos para este periodo" description="Selecciona otro rango de fechas para continuar." />}{status === "success" && stats && <EnergyChart data={series} stats={stats} />}</div></section>
    {stats && <div className="analysis-grid"><section className="insight-card"><div className="analysis-heading"><Activity /><div><p className="eyebrow">Datos calculados</p><h2>Análisis del mercado</h2></div></div><div className="insight-list">{stats.insights.items.map((item) => <article key={item.title} className={`insight-item ${item.kind}`}><span>{insightSymbol(item.kind)}</span><div><strong>{item.title}</strong><p>{item.text}</p></div></article>)}</div></section><section className="suggestion-card"><div className="analysis-heading"><Lightbulb /><div><p className="eyebrow">Sugerencia</p><h2>Mejor ventana observada</h2></div></div><p>{stats.insights.suggestion}</p><div className="suggestion-price"><span>{formatPointTime(stats.minimum)}</span><strong>{formatPrice(stats.minimum.price)} <small>€/MWh</small></strong></div><small>Basado únicamente en los precios del periodo seleccionado; no es una predicción.</small></section></div>}
  </AppLayout>;
}

function Metric({ icon: Icon, label, value, tone = "default", detail, loading }) { return <article className={`metric-card analytic ${tone}`}><span className={`metric-icon ${tone}`}><Icon /></span><div><p>{label}</p><strong>{loading ? "—" : formatPrice(value)} <small>€/MWh</small></strong>{!loading && detail && <span className="metric-detail">{detail}</span>}</div></article>; }
Metric.propTypes = { icon: PropTypes.elementType.isRequired, label: PropTypes.string.isRequired, value: PropTypes.number, tone: PropTypes.string, detail: PropTypes.string, loading: PropTypes.bool };
function formatPrice(value) { return Number.isFinite(value) ? value.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—"; }
function trendLabel(trend) { return trend === "positive" ? "Alcista" : trend === "negative" ? "Bajista" : "Estable"; }
function insightSymbol(kind) { return kind === "positive" ? "↗" : kind === "negative" ? "↘" : kind === "warning" ? "⚡" : "◎"; }
