import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { BarChart3, Boxes, LogOut, Menu, Plus, X, Zap } from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { deleteToken } from "../api/tokens";
import { useAuth } from "../features/auth/auth-context";
import ThemeToggle from "../features/theme/ThemeToggle";

const links = [
  { to: "/dashboard", label: "Resumen", icon: BarChart3 },
  { to: "/precios", label: "Mercados", icon: Zap },
  { to: "/productos", label: "Productos", icon: Boxes },
  { to: "/productos/create", label: "Nuevo producto", icon: Plus },
];

export default function AppLayout({ children }) {
  const auth = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);
  useEffect(() => {
    const closeOnEscape = (event) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);
  useEffect(() => {
    const desktop = window.matchMedia("(min-width: 901px)");
    const closeOnDesktop = (event) => {
      if (event.matches) setOpen(false);
    };
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, []);

  const handleSignOut = async () => {
    try {
      if (auth.getIdMongo()) await deleteToken();
    } catch {
      /* La sesión local siempre se cierra. */
    }
    auth.signOuth();
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/dashboard" className="brand">
          <span className="brand-mark">
            <Zap size={20} />
          </span>
          <span>WAC Energy</span>
        </NavLink>
        <nav
          id="main-navigation"
          className={`main-nav ${open ? "is-open" : ""}`}
          aria-label="Navegación principal"
        >
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/productos"}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="user-menu">
          <span className="system-status">
            <i />
            En línea
          </span>
          <ThemeToggle />
          <span className="user-avatar" aria-hidden="true">
            {auth.getUser().slice(0, 1).toUpperCase()}
          </span>
          <span className="user-name">{auth.getUser()}</span>
          <button
            type="button"
            className="icon-button"
            onClick={handleSignOut}
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
          >
            <LogOut size={18} />
          </button>
        </div>
        <button
          type="button"
          className="icon-button mobile-menu"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls="main-navigation"
          aria-label={open ? "Cerrar navegación" : "Abrir navegación"}
        >
          {open ? <X /> : <Menu />}
        </button>
      </header>
      {open && (
        <button
          className="nav-backdrop"
          type="button"
          onClick={() => setOpen(false)}
          aria-label="Cerrar navegación"
        />
      )}
      <main className="app-content">{children}</main>
    </div>
  );
}

AppLayout.propTypes = { children: PropTypes.node.isRequired };
