import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Zap } from "lucide-react";
import ThemeToggle from "../features/theme/ThemeToggle";

export default function PublicLayout({ children }) {
  return <div className="auth-shell"><header className="public-header"><Link to="/" className="brand"><span className="brand-mark"><Zap size={20} /></span>WAC Energy</Link><div className="public-actions"><ThemeToggle /><Link to="/registro" className="button button-ghost">Crear cuenta</Link></div></header><main>{children}</main></div>;
}
PublicLayout.propTypes = { children: PropTypes.node.isRequired };
