import axios from "axios";

const URL = `http://127.0.0.1:8000`
const endpoint = `${URL}/api/users`

export const AccessToken = (username, password) => axios.post(`${URL}/token`, new URLSearchParams({ username, password }));

export const VerifyToken = async (token) => await axios.post(`${URL}/verify-token`, { token });

export const RefreshToken = async (refreshToken) =>  await axios.post(`${URL}/refresh-token`, { refresh_token: refreshToken });

export const deleteToken = async (_id) => await axios.delete(`${URL}/delete-token`, {  data: { _id } } );

export const InfoUsuario = async (token) => await axios.get(`${URL}/users/me`, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});