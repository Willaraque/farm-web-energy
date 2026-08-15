import { apiClient } from "./client";


const endpoint = "/api/users";
export const createUser = (user) => apiClient.post(`${endpoint}/create`, user);
export const fetchUser = (id) => apiClient.get(`${endpoint}/${id}`);
export const updateUser = (id, user) =>
  apiClient.put(`${endpoint}/update/${id}`, user);
export const deleteUser = (id) => apiClient.delete(`${endpoint}/delete/${id}`);
