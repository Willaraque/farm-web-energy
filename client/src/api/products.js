import { apiClient } from "./client";

const endpoint = "/api/tasks";
export const fetchTasks = () => apiClient.get(endpoint);
export const fetchTask = (id) => apiClient.get(`${endpoint}/${id}`);
export const createTask = (task) => apiClient.post(endpoint, task);
export const updateTask = (id, task) =>
  apiClient.put(`${endpoint}/${id}`, task);
export const deleteTask = (id) => apiClient.delete(`${endpoint}/${id}`);
