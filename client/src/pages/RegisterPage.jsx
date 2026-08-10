import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/auth-context";
import { createUser } from "../api/users";
import { getApiError } from "../api/client";
import PublicLayout from "../layouts/PublicLayout";

const EMPTY_FORM = { name: "", surname: "", username: "", password: "", tel: "" };

export default function RegisterPage() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const auth = useAuth();
  const navigate = useNavigate();

  if (auth.isAutenticated) return <Navigate to="/dashboard" replace />;

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const submit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await createUser(form);
      navigate("/", { replace: true, state: { registered: true } });
    } catch (requestError) {
      setError(getApiError(requestError, "No se pudo crear la cuenta."));
    } finally {
      setSubmitting(false);
    }
  };

  return <PublicLayout><div className="auth-page centered"><section className="auth-card register-card">
    <p className="eyebrow">Nueva cuenta</p><h1>Empieza con WAC Energy</h1><p className="muted">Completa tus datos para acceder al espacio de trabajo.</p>
    <form onSubmit={submit}>
      <div className="form-grid"><label className="field">Nombre<input required name="name" autoComplete="given-name" value={form.name} onChange={update} /></label><label className="field">Apellidos<input required name="surname" autoComplete="family-name" value={form.surname} onChange={update} /></label></div>
      <label className="field">Correo o usuario<input required name="username" autoComplete="username" value={form.username} onChange={update} /></label>
      <label className="field">Teléfono<input name="tel" type="tel" autoComplete="tel" value={form.tel} onChange={update} /></label>
      <label className="field">Contraseña<input required name="password" type="password" minLength={8} autoComplete="new-password" value={form.password} onChange={update} /><small>Mínimo 8 caracteres.</small></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button button-primary button-full" disabled={submitting}>{submitting ? "Creando cuenta…" : "Crear cuenta"}</button>
    </form>
    <p className="auth-footer">¿Ya tienes cuenta? <Link to="/">Iniciar sesión</Link></p>
  </section></div></PublicLayout>;
}
