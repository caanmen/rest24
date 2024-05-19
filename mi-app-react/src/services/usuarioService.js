// src/services/usuarioService.js
import axios from 'axios';

const apiUrl = 'http://localhost:3300/usuarios';

export const getUsuarios = async () => {
  const response = await axios.get(apiUrl);
  return response.data;
};

export const createUsuario = async (usuario) => {
  const response = await axios.post(apiUrl, usuario);
  return response.data;
};

// Otros métodos para manejar usuarios...
