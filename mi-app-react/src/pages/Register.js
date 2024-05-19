// src/pages/Register.js
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { register } from '../services/auth';

const Register = () => {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [correo, setCorreo] = useState('');
  const [telefono, setTelefono] = useState('');
  const [tipoUsuario, setTipoUsuario] = useState('usuario'); // Valor predeterminado
  const [contrasena, setContrasena] = useState('');
  const history = useHistory();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await register({ nombre, apellido, correo, telefono, tipo_usuario: tipoUsuario, contrasena });
      history.push('/login'); // Redirigir a la página de login
    } catch (error) {
      console.error('Error en el registro:', error);
      alert('Error al crear el usuario');
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Nombre:
          <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        </label>
        <br />
        <label>
          Apellido:
          <input type="text" value={apellido} onChange={(e) => setApellido(e.target.value)} required />
        </label>
        <br />
        <label>
          Correo:
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
        </label>
        <br />
        <label>
          Teléfono:
          <input type="text" value={telefono} onChange={(e) => setTelefono(e.target.value)} required />
        </label>
        <br />
        <label>
          Tipo de Usuario:
          <select value={tipoUsuario} onChange={(e) => setTipoUsuario(e.target.value)}>
            <option value="usuario">Usuario</option>
            <option value="administrador">Administrador</option>
            <option value="super_administrador">Super Administrador</option>
          </select>
        </label>
        <br />
        <label>
          Contraseña:
          <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required />
        </label>
        <br />
        <button type="submit">Registrar</button>
      </form>
    </div>
  );
};

export default Register;
