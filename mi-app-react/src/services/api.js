// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3300', // Cambia esto según tu configuración
});

export const getMesas = () => api.get('/mesas');
export const createMesa = (mesa) => api.post('/mesas', mesa);
export const updateMesa = (numero_mesa, mesa) => api.put(`/mesas/${numero_mesa}`, mesa);
export const deleteMesa = (numero_mesa) => api.delete(`/mesas/${numero_mesa}`);

export default api;
