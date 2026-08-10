import axios from "axios";

export const apiClient = axios.create({
  // En desarrollo Vite redirige estas llamadas al backend. En despliegues
  // separados se configura VITE_API_URL sin cambiar el código fuente.
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

export function getApiError(error, fallback = "No se pudo completar la operación.") {
  return error?.response?.data?.detail || (error?.code === "ECONNABORTED" ? "La solicitud tardó demasiado." : fallback);
}
