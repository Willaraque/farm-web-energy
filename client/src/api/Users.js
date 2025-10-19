import axios from "axios";

const URL = `http://13.38.10.75:3000`
const endpoint = `${URL}/api/users`

export const createUser = (newUser) => axios.post(`${endpoint}/create`, newUser); //esta funcion si la utilizamos

export const OneUser = async (id) => await axios.get(`${endpoint}/${id}`);

export const updateUser = (id, user) => axios.put(`${endpoint}/update/${id}`, user)

export const deleteUser = (id) => axios.delete(`${endpoint}/delete/${id}`)