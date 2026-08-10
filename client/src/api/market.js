import { apiClient } from "./client";

export const fetchMarketData = (filters) => apiClient.post("/market-data", filters);
