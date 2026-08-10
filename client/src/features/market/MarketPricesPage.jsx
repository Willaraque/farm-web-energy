import { useMemo, useState } from "react";
import PropTypes from "prop-types";
import { Download, Search } from "lucide-react";
import { fetchMarketData } from "../../api/market";
import { getApiError } from "../../api/client";
import AppLayout from "../../layouts/AppLayout";
import DataTable from "../../components/data-table/DataTable";
import PageHeader from "../../components/PageHeader";
import SpinnerLoader from "../../components/SpinnerLoader";
import StatePanel from "../../components/StatePanel";
import { calculatePriceStats } from "./market-data";

export default function MarketPricesPage() {
  const [filters, setFilters] = useState({ desde: "", hasta: "", tipo: "Precios-OMIE", mercados: ["diario"] });
  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const columns = useMemo(() => rows[0] ? Object.keys(rows[0]).map((key) => ({ accessorKey: key, header: key.replaceAll("_", " "), meta: { label: key.replaceAll("_", " ") }, cell: ({ getValue }) => formatValue(key, getValue()) })) : [], [rows]);
  const stats = useMemo(() => calculatePriceStats(rows), [rows]);

  const submit = async (event) => {
    event.preventDefault(); setStatus("loading"); setError("");
    try { const { data } = await fetchMarketData(filters); const next = Array.isArray(data) ? data : []; setRows(next); setStatus(next.length ? "success" : "empty"); }
    catch (requestError) { setError(getApiError(requestError, "No se pudieron obtener los precios.")); setStatus("error"); }
  };
  const updateDate = (key, value) => { setFilters({ ...filters, [key]: value }); setRows([]); setStatus("idle"); };
  const download = () => {
    const headers = Object.keys(rows[0]);
    const escape = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
    const csv = `\uFEFF${headers.map(escape).join(",")}\n${rows.map((row) => headers.map((header) => escape(row[header])).join(",")).join("\n")}`;
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a"); link.href = url; link.download = `precios-${filters.desde}-${filters.hasta}.csv`; link.click(); URL.revokeObjectURL(url);
  };

  return <AppLayout>
    <PageHeader eyebrow="Mercados" title="Precios de energía" description="Consulta, filtra y exporta los datos del periodo seleccionado." actions={rows.length > 0 && <button className="button button-secondary" onClick={download}><Download size={16} />Exportar CSV</button>} />
    <form className="filter-card market-filters" onSubmit={submit}>
      <label className="field compact">Desde<input required type="date" value={filters.desde} max={filters.hasta || undefined} onChange={(event) => updateDate("desde", event.target.value)} /></label>
      <label className="field compact">Hasta<input required type="date" value={filters.hasta} min={filters.desde || undefined} onChange={(event) => updateDate("hasta", event.target.value)} /></label>
      <label className="field compact">Mercado<select value={filters.mercados[0]} onChange={(event) => setFilters({ ...filters, mercados: [event.target.value] })}><option value="diario">Diario</option><option value="intradiario">Intradiario</option></select></label>
      <button className="button button-primary" disabled={status === "loading"}><Search size={16} />Consultar</button>
    </form>
    {stats && <div className="metric-grid compact-metrics"><Stat label="Mínimo" value={stats.minimum} /><Stat label="Promedio" value={stats.average} /><Stat label="Máximo" value={stats.maximum} /></div>}
    {status === "loading" && <div className="panel"><SpinnerLoader label="Consultando precios" /></div>}
    {status === "error" && <StatePanel type="error" title="Error en la consulta" description={error} />}
    {status === "empty" && <StatePanel title="Sin datos en el periodo" description="Prueba con otro rango o mercado." />}
    {status === "idle" && <StatePanel title="Prepara tu consulta" description="Selecciona un rango de fechas y el mercado que quieres analizar." />}
    {status === "success" && <DataTable columns={columns} data={rows} searchPlaceholder="Buscar fecha, tipo, hora o precio…" pageSize={15} />}
  </AppLayout>;
}

function formatValue(key, value) { return key.toLowerCase().includes("precio") && Number.isFinite(Number(value)) ? `${Number(value).toFixed(2)} €` : String(value ?? "—"); }
function Stat({ label, value }) { return <article className="metric-card mini"><div><p>{label}</p><strong>{value.toFixed(2)} <small>€/MWh</small></strong></div></article>; }
Stat.propTypes = { label: PropTypes.string.isRequired, value: PropTypes.number.isRequired };
