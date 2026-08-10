import { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { Activity, ArrowDown, ArrowUp, RefreshCw } from "lucide-react";
import { fetchMarketData } from "../../api/market";
import { getApiError } from "../../api/client";
import { createMarketSeries } from "../market/market-data";
import AppLayout from "../../layouts/AppLayout";
import EnergyChart from "./EnergyChart";
import PageHeader from "../../components/PageHeader";
import SpinnerLoader from "../../components/SpinnerLoader";
import StatePanel from "../../components/StatePanel";

const today = () => new Date().toISOString().slice(0, 10);

export default function DashboardPage() {
  const [filters, setFilters] = useState({
    desde: today(),
    hasta: today(),
    tipo: "Precios-OMIE",
    mercados: ["diario"],
  });
  const [series, setSeries] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setStatus("loading");
    setError("");

    try {
      const { data } = await fetchMarketData(filters);
      const nextSeries = createMarketSeries(data, "diario");
      setSeries(nextSeries);
      setStatus(nextSeries.length ? "success" : "empty");
    } catch (requestError) {
      setSeries([]);
      setError(getApiError(requestError, "No se pudieron cargar los precios."));
      setStatus("error");
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  const stats = summarizeSeries(series);

  return (
    <AppLayout>
      <PageHeader
        eyebrow="Visión general"
        title="Panel de energía"
        description="Evolución y señales clave del mercado diario."
        actions={
          <button
            className="button button-secondary"
            type="button"
            onClick={load}
            disabled={status === "loading"}
          >
            <RefreshCw size={16} />
            Actualizar
          </button>
        }
      />

      <div className="filter-card">
        <label className="field compact">
          Desde
          <input
            type="date"
            value={filters.desde}
            max={filters.hasta}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                desde: event.target.value,
              }))
            }
          />
        </label>
        <label className="field compact">
          Hasta
          <input
            type="date"
            value={filters.hasta}
            min={filters.desde}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                hasta: event.target.value,
              }))
            }
          />
        </label>
      </div>

      <div className="metric-grid">
        <Metric
          icon={Activity}
          label="Precio medio"
          value={stats?.average}
          loading={status === "loading"}
        />
        <Metric
          icon={ArrowDown}
          label="Mínimo"
          value={stats?.minimum}
          tone="positive"
          loading={status === "loading"}
        />
        <Metric
          icon={ArrowUp}
          label="Máximo"
          value={stats?.maximum}
          tone="warning"
          loading={status === "loading"}
        />
      </div>

      <section className="chart-card">
        <div className="section-heading">
          <div>
            <h2>Mercado diario</h2>
            <p>Precio horario para el periodo seleccionado.</p>
          </div>
        </div>
        <div className="chart-area">
          {status === "loading" && <SpinnerLoader label="Cargando mercado" />}
          {status === "error" && (
            <StatePanel
              type="error"
              title="No se pudieron cargar los datos"
              description={error}
              action={
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={load}
                >
                  Reintentar
                </button>
              }
            />
          )}
          {status === "empty" && (
            <StatePanel
              title="No hay datos para este periodo"
              description="Selecciona otro rango de fechas para continuar."
            />
          )}
          {status === "success" && <EnergyChart data={series} />}
        </div>
      </section>
    </AppLayout>
  );
}

function Metric({ icon: Icon, label, value, tone = "default", loading = false }) {
  const formattedValue =
    typeof value === "number" && Number.isFinite(value)
      ? value.toLocaleString("es-ES", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })
      : "—";

  return (
    <article className="metric-card">
      <span className={`metric-icon ${tone}`}>
        <Icon />
      </span>
      <div>
        <p>{label}</p>
        <strong>
          {loading ? "—" : formattedValue} <small>€/MWh</small>
        </strong>
      </div>
    </article>
  );
}

Metric.propTypes = {
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.number,
  tone: PropTypes.string,
  loading: PropTypes.bool,
};

function summarizeSeries(data) {
  if (!data.length) return null;

  let total = 0;
  let minimum = Infinity;
  let maximum = -Infinity;
  let count = 0;

  for (const point of data) {
    const price = Number(point.price);
    if (!Number.isFinite(price)) continue;

    total += price;
    minimum = Math.min(minimum, price);
    maximum = Math.max(maximum, price);
    count += 1;
  }

  if (!count) return null;

  return {
    average: total / count,
    minimum,
    maximum,
  };
}
