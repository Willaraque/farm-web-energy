import { apiClient } from "./client";

export const AccessToken = (username, password) =>
  apiClient.post("/token", new URLSearchParams({ username, password }), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
export const VerifyToken = () => apiClient.post("/verify-token");
export const deleteToken = () => apiClient.delete("/delete-token");
export const fetchCurrentUser = (token) =>
  apiClient.get("/users/me", { headers: { Authorization: `Bearer ${token}` } });
export const requestPasswordOtp = (phone) =>
  apiClient.post("/auth/password/forgot", { phone });
export const verifyPasswordOtp = (phone, challengeId, code) =>
  apiClient.post("/auth/password/verify-otp", {
    phone,
    challenge_id: challengeId,
    code,
  });
export const resetPassword = (resetToken, password) =>
  apiClient.post("/auth/password/reset", { reset_token: resetToken, password });
export const fetchOAuthProviders = () => apiClient.get("/auth/oauth/providers");
export const exchangeOAuthCode = (code) =>
  apiClient.post("/auth/oauth/exchange", { code });
export const oauthStartUrl = (provider) =>
  `${import.meta.env.VITE_API_URL || ""}/auth/oauth/${provider}/start`;
