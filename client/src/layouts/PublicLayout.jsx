import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Zap } from "lucide-react";
import ThemeToggle from "../features/theme/ThemeToggle";

export default function PublicLayout({ children }) {
  return (
    <div className="auth-shell">
      <header className="public-header">
        <Link to="/" className="brand public-brand" aria-label="WAC Energy, inicio">
          <span className="brand-mark">
            <Zap size={20} />
          </span>
          WAC Energy
        </Link>
        <nav className="public-actions" aria-label="Navegación de acceso">
          <ThemeToggle />
          <Link to="/registro" className="button button-ghost">
            Crear cuenta
          </Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
PublicLayout.propTypes = { children: PropTypes.node.isRequired };
