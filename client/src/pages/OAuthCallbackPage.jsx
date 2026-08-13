import { useEffect, useState } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import PublicLayout from "../layouts/PublicLayout";
import SpinnerLoader from "../components/SpinnerLoader";
import { exchangeOAuthCode } from "../api/tokens";
import { getApiError } from "../api/client";
import { useAuth } from "../features/auth/auth-context";

export default function OAuthCallbackPage() {
  const [params] = useSearchParams();
  const [error, setError] = useState("");
  const auth = useAuth();
  const navigate = useNavigate();
  const code = params.get("code");
  useEffect(() => {
    if (!code) {
      setError("La respuesta del proveedor no contiene un código válido.");
      return;
    }
    exchangeOAuthCode(code)
      .then((response) => {
        auth.saveUser(response);
        navigate("/dashboard", { replace: true });
      })
      .catch((requestError) =>
        setError(
          getApiError(requestError, "No se pudo completar el acceso social."),
        ),
      );
  }, [auth, code, navigate]);
  if (auth.isAutenticated) return <Navigate to="/dashboard" replace />;
  return (
    <PublicLayout>
      <div className="auth-page centered">
        <section className="auth-card register-card">
          {error ? (
            <>
              <p className="form-error" role="alert">
                {error}
              </p>
              <a className="button button-secondary button-full" href="/">
                Volver al login
              </a>
            </>
          ) : (
            <SpinnerLoader label="Verificando identidad" />
          )}
        </section>
      </div>
    </PublicLayout>
  );
}
