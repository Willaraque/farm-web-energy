import { apiClient } from "./client";



export const AccessToken = (username, password) => apiClient.post("/token", new URLSearchParams({ username, password }), { headers: { "Content-Type": "application/x-www-form-urlencoded" } });
export const VerifyToken = (token) => apiClient.post("/verify-token", { token });
export const deleteToken = (_id) => apiClient.delete("/delete-token", { data: { _id } });
export const fetchCurrentUser = (token) => apiClient.get("/users/me", { headers: { Authorization: `Bearer ${token}` } });
