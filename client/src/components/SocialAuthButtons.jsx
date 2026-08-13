import { useEffect, useState } from "react";
import { fetchOAuthProviders, oauthStartUrl } from "../api/tokens";

const labels = { google: "Google", facebook: "Facebook", instagram: "Instagram" };
const logos = { google: GoogleLogo, facebook: FacebookLogo, instagram: InstagramLogo };

export default function SocialAuthButtons() {
  const [providers, setProviders] = useState([]);
  useEffect(() => { fetchOAuthProviders().then(({ data }) => setProviders(data.providers || [])).catch(() => setProviders([])); }, []);
  return <div className="auth-alternatives"><span>o continúa con</span><div className="social-buttons">{Object.keys(labels).map((provider) => {
    const enabled = providers.includes(provider);
    const Logo = logos[provider];
    const content = <><i aria-hidden="true"><Logo /></i>{!enabled && <small aria-hidden="true">!</small>}</>;
    return enabled
      ? <a key={provider} className={`button button-secondary social-button ${provider}`} href={oauthStartUrl(provider)} aria-label={`Continuar con ${labels[provider]}`} title={`Continuar con ${labels[provider]}`}>{content}</a>
      : <button key={provider} type="button" className={`button button-secondary social-button ${provider} is-unconfigured`} onClick={() => window.alert(`El acceso con ${labels[provider]} no está configurado en este momento.`)} aria-label={`${labels[provider]} no está configurado`} title={`${labels[provider]} todavía no está configurado`}>{content}</button>;
  })}</div></div>;
}

function GoogleLogo() { return <svg viewBox="0 0 24 24"><path fill="#4285F4" d="M21.6 12.23c0-.71-.06-1.4-.18-2.06H12v3.9h5.38a4.6 4.6 0 0 1-2 3.02v2.53h3.24c1.9-1.75 2.98-4.33 2.98-7.39Z"/><path fill="#34A853" d="M12 22c2.7 0 4.97-.9 6.62-2.38l-3.24-2.53c-.9.6-2.04.96-3.38.96-2.6 0-4.81-1.76-5.6-4.13H3.06v2.61A10 10 0 0 0 12 22Z"/><path fill="#FBBC05" d="M6.4 13.92A6 6 0 0 1 6.08 12c0-.67.12-1.32.32-1.92V7.47H3.06A10 10 0 0 0 2 12c0 1.63.39 3.17 1.06 4.53l3.34-2.61Z"/><path fill="#EA4335" d="M12 5.95c1.47 0 2.79.5 3.83 1.5l2.87-2.87A9.63 9.63 0 0 0 12 2a10 10 0 0 0-8.94 5.47l3.34 2.61c.79-2.37 3-4.13 5.6-4.13Z"/></svg>; }
function FacebookLogo() { return <svg viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12a12 12 0 1 0-13.88 11.85v-8.47H7.08V12h3.04V9.43c0-3 1.79-4.66 4.53-4.66.9.01 1.8.09 2.68.24v2.95h-1.51c-1.49 0-1.95.92-1.95 1.87V12h3.32l-.53 3.38h-2.79v8.47A12 12 0 0 0 24 12Z"/><path fill="#fff" d="m16.66 15.38.53-3.38h-3.32V9.83c0-.95.46-1.87 1.95-1.87h1.51V5.01a18.2 18.2 0 0 0-2.68-.24c-2.74 0-4.53 1.66-4.53 4.66V12H7.08v3.38h3.04v8.47a12.2 12.2 0 0 0 3.75 0v-8.47h2.79Z"/></svg>; }
function InstagramLogo() { return <svg viewBox="0 0 24 24"><defs><linearGradient id="instagram-gradient" x1="0" y1="1" x2="1" y2="0"><stop stopColor="#FFDC80"/><stop offset=".35" stopColor="#F56040"/><stop offset=".68" stopColor="#C13584"/><stop offset="1" stopColor="#405DE6"/></linearGradient></defs><rect x="2" y="2" width="20" height="20" rx="6" fill="url(#instagram-gradient)"/><circle cx="12" cy="12" r="4.25" fill="none" stroke="#fff" strokeWidth="1.8"/><circle cx="17.4" cy="6.7" r="1.15" fill="#fff"/></svg>; }
