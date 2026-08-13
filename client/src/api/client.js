import axios from "axios";

export const apiClient = axios.create({
  // En desarrollo Vite redirige estas llamadas al backend. En despliegues
  // separados se configura VITE_API_URL sin cambiar el código fuente.
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  try {
    const session = JSON.parse(localStorage.getItem("energy-session"));
    if (session?.accessToken && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
  } catch {
    /* An invalid local session is handled by AuthProvider. */
  }
  return config;
});

export function getApiError(
  error,
  fallback = "No se pudo completar la operación.",
) {
  if (error?.code === "ECONNABORTED") return "La solicitud tardó demasiado.";
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return null;
        const field = Array.isArray(item.loc)
          ? item.loc
              .filter((part) => !["body", "query", "path"].includes(part))
              .join(".")
          : "";
        return [field, item.msg].filter(Boolean).join(": ");
      })
      .filter(Boolean);
    if (messages.length) return messages.join(" · ");
  }
  if (detail && typeof detail === "object") {
    return typeof detail.msg === "string" ? detail.msg : fallback;
  }
  return fallback;
}
