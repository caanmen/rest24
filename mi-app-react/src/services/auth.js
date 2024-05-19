// src/services/auth.js
import axios from 'axios';

const authApi = axios.create({
  baseURL: 'http://localhost:3200', // Cambia esto según tu configuración
});

export const login = (credentials) => authApi.post('/login', credentials);
export const register = (user) => authApi.post('/create_user', user);

export default authApi;
