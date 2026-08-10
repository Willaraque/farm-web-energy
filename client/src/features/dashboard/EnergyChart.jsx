import PropTypes from "prop-types";
import { Line } from "react-chartjs-2";
import { CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from "chart.js";
import { useTheme } from "../theme/theme-context";
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Title, Tooltip, Legend);
export default function EnergyChart({ data }) {
  const { resolvedTheme } = useTheme();
  const dark = resolvedTheme === "dark";
  const chartData = { labels: data.map((entry) => entry.date), datasets: [{ label: "Precio (€/MWh)", data: data.map((entry) => entry.price), borderColor: dark ? "#b8ff3d" : "#0f9f6e", backgroundColor: dark ? "rgba(184,255,61,.10)" : "rgba(15,159,110,.10)", pointRadius: data.length > 48 ? 0 : 2, borderWidth: 2, tension: .25, fill: true }] };
  const tickColor = dark ? "#91a5a0" : "#64748b";
  const options = { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: "index" }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (item) => `${item.raw.toFixed(2)} €/MWh` } } }, scales: { x: { grid: { display: false }, ticks: { color: tickColor, maxTicksLimit: 12 } }, y: { grid: { color: dark ? "rgba(122,255,218,.10)" : "rgba(100,116,139,.16)" }, ticks: { color: tickColor, callback: (value) => `${value} €` } } } };
  return <Line data={chartData} options={options} />;
}
EnergyChart.propTypes = { data: PropTypes.arrayOf(PropTypes.shape({ date: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired, price: PropTypes.number.isRequired })).isRequired };
