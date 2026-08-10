import { useState } from "react";
import { Eye, EyeOff, LockKeyhole, Zap } from "lucide-react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/auth-context";
import { AccessToken } from "../api/tokens";
import { getApiError } from "../api/client";
import PublicLayout from "../layouts/PublicLayout";

export default function LoginPage() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (auth.isAutenticated) return <Navigate to="/dashboard" replace />;

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const response = await AccessToken(form.username.trim(), form.password);
      auth.saveUser(response);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (requestError) {
      setError(getApiError(requestError, "Usuario o contraseña incorrectos."));
    } finally {
      setSubmitting(false);
    }
  };

  return <PublicLayout><div className="auth-page">
    <section className="auth-intro" aria-label="WAC Energy">
      <span className="hero-icon"><Zap /></span><p className="eyebrow">Inteligencia energética</p>
      <h1>Decisiones claras para un mercado que no se detiene.</h1>
      <p>Consulta precios, productos e indicadores operativos desde un único espacio seguro.</p>
      <div className="auth-proof"><span>Datos centralizados</span><span>Seguimiento diario</span><span>Acceso seguro</span></div>
    </section>
    <section className="auth-card" aria-labelledby="login-title">
      <div className="auth-card-heading"><span className="icon-surface"><LockKeyhole /></span><div><p className="eyebrow">Bienvenido de nuevo</p><h2 id="login-title">Inicia sesión</h2></div></div>
      <form onSubmit={submit} noValidate>
        <label className="field">Correo o usuario<input required autoComplete="username" autoFocus value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="nombre@empresa.com" /></label>
        <label className="field">Contraseña<span className="password-field"><input required minLength={6} type={showPassword ? "text" : "password"} autoComplete="current-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Tu contraseña" /><button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}>{showPassword ? <EyeOff /> : <Eye />}</button></span></label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button button-primary button-full" disabled={submitting || !form.username || !form.password}>{submitting ? <><span className="spinner small" />Accediendo…</> : "Acceder al panel"}</button>
      </form>
      <p className="auth-footer">¿Aún no tienes acceso? <Link to="/registro">Crear cuenta</Link></p>
    </section>
  </div></PublicLayout>;
}
