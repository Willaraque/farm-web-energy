import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { KeyRound } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import PublicLayout from "../layouts/PublicLayout";
import { getApiError } from "../api/client";
import {
  requestPasswordOtp,
  resetPassword,
  verifyPasswordOtp,
} from "../api/tokens";

export default function PhoneAuthPage() {
  const [step, setStep] = useState("phone");
  const [prefix, setPrefix] = useState("+34");
  const [number, setNumber] = useState("");
  const [challenge, setChallenge] = useState("");
  const [code, setCode] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [passwords, setPasswords] = useState({ password: "", confirm: "" });
  const [resend, setResend] = useState(0);
  const [expires, setExpires] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const phone = `${prefix}${number}`;
  useEffect(() => {
    if (!resend && !expires) return;
    const timer = setInterval(() => {
      setResend((value) => Math.max(0, value - 1));
      setExpires((value) => Math.max(0, value - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [resend, expires]);
  const send = async () => {
    setBusy(true);
    setError("");
    try {
      const { data } = await requestPasswordOtp(phone);
      setChallenge(data.challenge_id);
      setResend(data.resend_in);
      setExpires(data.expires_in);
      setCode("");
      setStep("otp");
    } catch (requestError) {
      setError(getApiError(requestError));
    } finally {
      setBusy(false);
    }
  };
  const verify = async () => {
    setBusy(true);
    setError("");
    try {
      const { data } = await verifyPasswordOtp(phone, challenge, code);
      setResetToken(data.reset_token);
      setStep("password");
    } catch (requestError) {
      setError(getApiError(requestError));
    } finally {
      setBusy(false);
    }
  };
  const finish = async () => {
    if (passwords.password !== passwords.confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await resetPassword(resetToken, passwords.password);
      navigate("/", { replace: true, state: { passwordReset: true } });
    } catch (requestError) {
      setError(getApiError(requestError));
    } finally {
      setBusy(false);
    }
  };
  const submit = (event) => {
    event.preventDefault();
    if (step === "phone") send();
    else if (step === "otp") verify();
    else finish();
  };
  return (
    <PublicLayout>
      <div className="auth-page centered">
        <section className="auth-card register-card auth-flow-card">
          <div className="auth-card-heading">
            <span className="icon-surface">
              <KeyRound />
            </span>
            <div>
              <p className="eyebrow">Acceso seguro</p>
              <h1>Recupera tu contraseña</h1>
            </div>
          </div>
          <form onSubmit={submit}>
            {step === "phone" && (
              <label className="field">
                Número de teléfono
                <div className="phone-fields">
                  <select
                    aria-label="Prefijo internacional"
                    value={prefix}
                    onChange={(event) => setPrefix(event.target.value)}
                  >
                    <option value="+34">+34</option>
                    <option value="+33">+33</option>
                    <option value="+44">+44</option>
                    <option value="+49">+49</option>
                    <option value="+1">+1</option>
                  </select>
                  <input
                    required
                    type="tel"
                    inputMode="numeric"
                    autoComplete="tel-national"
                    pattern="[1-9][0-9]{7,14}"
                    value={number}
                    onChange={(event) =>
                      setNumber(event.target.value.replace(/\D/g, ""))
                    }
                    placeholder="600123456"
                  />
                </div>
                <small>
                  Te enviaremos un código si existe una cuenta asociada.
                </small>
              </label>
            )}
            {step === "otp" && (
              <>
                <p className="muted otp-copy">
                  Introduce el código enviado a{" "}
                  <strong>{maskPhone(phone)}</strong>
                </p>
                <OtpInput value={code} onChange={setCode} />
                <p className="otp-timer">
                  Código válido durante {formatTime(expires)}
                </p>
                <button
                  type="button"
                  className="button button-ghost resend-button"
                  disabled={resend > 0 || busy}
                  onClick={send}
                >
                  {resend ? `Reenviar código en ${resend}s` : "Reenviar código"}
                </button>
              </>
            )}
            {step === "password" && (
              <>
                <label className="field">
                  Nueva contraseña
                  <input
                    required
                    minLength="10"
                    type="password"
                    autoComplete="new-password"
                    value={passwords.password}
                    onChange={(event) =>
                      setPasswords({
                        ...passwords,
                        password: event.target.value,
                      })
                    }
                  />
                </label>
                <label className="field">
                  Confirmar contraseña
                  <input
                    required
                    minLength="10"
                    type="password"
                    autoComplete="new-password"
                    value={passwords.confirm}
                    onChange={(event) =>
                      setPasswords({
                        ...passwords,
                        confirm: event.target.value,
                      })
                    }
                  />
                </label>
              </>
            )}
            {error && (
              <p className="form-error" role="alert">
                {error}
              </p>
            )}
            <button
              className="button button-primary button-full"
              disabled={busy || (step === "otp" && code.length !== 6)}
            >
              {busy
                ? "Procesando…"
                : step === "phone"
                  ? "Enviar código"
                  : step === "otp"
                    ? "Verificar código"
                    : "Cambiar contraseña"}
            </button>
          </form>
          <p className="auth-footer">
            <Link to="/">Volver al inicio de sesión</Link>
          </p>
        </section>
      </div>
    </PublicLayout>
  );
}

function OtpInput({ value, onChange }) {
  const refs = useRef([]);
  const digits = Array.from({ length: 6 }, (_, index) => value[index] || "");
  const update = (index, next) => {
    const chars = digits;
    chars[index] = next.slice(-1).replace(/\D/g, "");
    onChange(chars.join(""));
    if (chars[index] && index < 5) refs.current[index + 1]?.focus();
  };
  const paste = (event) => {
    const next = event.clipboardData
      .getData("text")
      .replace(/\D/g, "")
      .slice(0, 6);
    if (next) {
      event.preventDefault();
      onChange(next);
      refs.current[Math.min(next.length, 6) - 1]?.focus();
    }
  };
  return (
    <div className="otp-boxes" onPaste={paste}>
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(node) => {
            refs.current[index] = node;
          }}
          aria-label={`Dígito ${index + 1}`}
          inputMode="numeric"
          autoComplete={index === 0 ? "one-time-code" : "off"}
          maxLength="1"
          value={digit}
          onChange={(event) => update(index, event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Backspace" && !digit && index > 0)
              refs.current[index - 1]?.focus();
          }}
        />
      ))}
    </div>
  );
}
OtpInput.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};
function maskPhone(phone) {
  return `${phone.slice(0, 3)} ••• ••• ${phone.slice(-3)}`;
}
function formatTime(seconds) {
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}
