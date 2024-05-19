// src/pages/Login.js
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { login } from '../services/auth';

const Login = () => {
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const history = useHistory();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await login({ correo, contrasena });
      localStorage.setItem('token', response.data.access_token);
      history.push('/'); // Redirigir a la página de inicio
    } catch (error) {
      console.error('Error en el login:', error);
      alert('Credenciales inválidas');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Correo:
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
        </label>
        <br />
        <label>
          Contraseña:
          <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required />
        </label>
        <br />
        <button type="submit">Iniciar Sesión</button>
      </form>
    </div>
  );
};

export default Login;
