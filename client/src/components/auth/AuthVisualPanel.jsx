import PropTypes from "prop-types";
import { Activity, Database, ShieldCheck } from "lucide-react";

export default function AuthVisualPanel({ image, title, description, compact = false }) {
  return <aside className={`auth-visual-panel ${compact ? "compact" : ""}`}>
    <img src={image} alt="" width="1600" height="1000" loading="lazy" />
    <div className="auth-visual-copy"><span className="energy-kicker"><Activity />Ecosistema WAC Energy</span><h2>{title}</h2><p>{description}</p>{!compact && <div className="auth-visual-features"><span><Database />Datos centralizados</span><span><Activity />Seguimiento del mercado</span><span><ShieldCheck />Acceso seguro</span></div>}</div>
  </aside>;
}
AuthVisualPanel.propTypes = { image: PropTypes.string.isRequired, title: PropTypes.string.isRequired, description: PropTypes.string.isRequired, compact: PropTypes.bool };
