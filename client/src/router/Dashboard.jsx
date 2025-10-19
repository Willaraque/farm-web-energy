import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "../Autenticacion/AuthProvider";
import LogingOut from "../router/LogingOut";
import EnergyChart from "../components/GraficoDinamico"; // tu gráfico existente

// Utils
const todayStr = () => new Date().toISOString().split("T")[0];

// Paleta neón
const C = {
  bg: "#0b0b0f",
  panel: "#12121a",
  text: "#e6e6f0",
  sub: "#9aa0aa",
  cian: "#00E5FF",
  verde: "#39FF14",
  magenta: "#FF00F5",
  amarillo: "#F9F871",
  bord: "#1f2330",
};

export default function EnergyDashboardNeon() {
  // auth por si quieres usarlo
  const auth = useAuth();

  // Filtros
  const [desde, setDesde] = useState(todayStr());
  const [hasta, setHasta] = useState(todayStr());

  // Datos
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // KPIs derivados
  const { mean, min, max } = useMemo(() => {
    if (!series.length) return { mean: 0, min: 0, max: 0 };
    const arr = series.map((d) => d.price);
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    return { mean, min: Math.min(...arr), max: Math.max(...arr) };
  }, [series]);

  // Fetch datos del backend (tu endpoint actual)
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const body = { desde, hasta, mercado: "Precios-OMIE", mercados: ["diario"] };
      const res = await fetch("http://127.0.0.1:8000/market-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();

      const transformed = Array.isArray(raw)
        ? raw
            .filter((r) => r.Mercado === "diario")
            .map((r) => ({ date: r.Hora, price: Number(r.Precio_Español) }))
        : [];

      setSeries(transformed);
    } catch (e) {
      console.error(e);
      setError("No se pudieron cargar datos. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  }, [desde, hasta]);

  // Primera carga
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <LogingOut>
      <div style={{ ...page, background: C.bg }}>
        <style>{cssNeon(C)}</style>

        {/* Columna izquierda: hero */}
        <div style={leftCol}>
          <div style={heroCard}>
            <h1 className="neon-title">Energy Dashboard</h1>
            <p className="sub">Panel minimalista en tema oscuro con acentos neón.</p>
          </div>
        </div>

        {/* Columna derecha: panel */}
        <div style={rightPanel}>
          <h3 className="panel-title">Precio de la Energía del Mercado Diario</h3>

          {/* KPIs */}
          <div className="kpis">
            <KPI label="Precio medio" value={`${mean.toFixed(2)} €/MWh`} accent={C.magenta} />
            <KPI label="Mínimo" value={`${min.toFixed(2)} €/MWh`} accent={C.verde} />
            <KPI label="Máximo" value={`${max.toFixed(2)} €/MWh`} accent={C.cian} />
          </div>

          {/* Filtros */}
          <div className="filters">
            <input className="date" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
            <input className="date" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
            <button className="btn btn-cian" onClick={fetchData}>Actualizar</button>
          </div>

          {/* Estado */}
          {error && <div className="alert">{error}</div>}
          {loading && <div className="loading">Cargando datos…</div>}

          {/* Gráfico principal */}
          {!loading && series.length > 0 && (
            <div className="chart-wrap">
              <EnergyChart data={series} />
            </div>
          )}

          {/* Min/Max inline */}
          {!loading && series.length > 0 && (
            <div className="minmax">
              <span>Mín: <b>{min.toFixed(2)} €/MWh</b></span>
              <span>Máx: <b>{max.toFixed(2)} €/MWh</b></span>
            </div>
          )}
        </div>
      </div>
    </LogingOut>
  );
}

/* ---------- UI bits ---------- */
function KPI({ label, value, accent }) {
  return (
    <div className="kpi">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value" style={{ textShadow: `0 0 18px ${accent}` }}>{value}</span>
    </div>
  );
}

/* ---------- Layout/CSS ---------- */
const page = {
  display: "flex",
  gap: 24,
  alignItems: "stretch",
  justifyContent: "space-between",
  padding: 20,
  minHeight: "100vh",
  boxSizing: "border-box",
  color: C.text,
};

const leftCol = { flex: 1, display: "flex", alignItems: "center", justifyContent: "center" };
const rightPanel = { flex: 1.4, background: C.panel, borderRadius: 14, border: `1px solid ${C.bord}`, boxShadow: "0 0 40px rgba(0,0,0,.35)", padding: 20 };

// 🔧 Aquí estaba el fallo de comillas/backtick en tu captura (cerramos con backtick, no con comillas)
const heroCard = {
  background: "linear-gradient(135deg, rgba(0, 229, 255, 0.08), rgba(255, 0, 245, 0.08))",
  border: `1px solid ${C.bord}`,
  padding: 24,
  borderRadius: 14,
  maxWidth: "90%",
  boxShadow: "0 0 40px rgba(0,0,0,.35), inset 0 0 20px rgba(255,255,255,.03)",
  textAlign: "center",
};

function cssNeon(p) {
  return `
    .panel-title{ font-weight:700; letter-spacing:.2px; color:${p.text}; margin-bottom:8px; }
    .sub{ color:${p.sub}; }
    .neon-title{ font-size: clamp(28px, 4.5vw, 56px); font-weight:800; color:${p.text}; text-shadow: 0 0 16px ${p.cian}, 0 0 6px ${p.magenta}; margin:0 0 10px 0; }
    .kpis{ display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:12px; margin:16px 0 8px 0; }
    .kpi{ background:#0f1118; border:1px solid ${p.bord}; border-radius:12px; padding:12px 14px; }
    .kpi-label{ font-size:12px; color:${p.sub}; }
    .kpi-value{ display:block; font-size:22px; font-weight:700; color:${p.text}; }
    .filters{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin:8px 0 12px 0; }
    .date{ background:#0f1118; color:${p.text}; border:1px solid #2a2f3a; padding:10px 12px; border-radius:10px; }
    .btn{ border:none; border-radius:10px; padding:10px 16px; font-weight:700; cursor:pointer; }
    .btn-cian{ background:${p.cian}; color:#00131a; box-shadow:0 0 22px ${p.cian}55; }
    .chart-wrap{ background:#0b0d14; border:1px solid ${p.bord}; border-radius:12px; padding:10px; margin-top:6px; }
    .loading{ color:${p.sub}; margin:10px 0; }
    .alert{ background:#2a0d17; border:1px solid #ff4d6d55; color:#ff91a3; padding:10px 12px; border-radius:10px; margin:8px 0; }
    .minmax{ display:flex; gap:16px; color:${p.sub}; margin-top:10px; }
    @media (max-width: 960px){ .kpis{ grid-template-columns:1fr; } }
  `;
}
