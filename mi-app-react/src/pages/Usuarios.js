import React, { useState, useEffect } from 'react';
import { obtenerUsuarios } from '../services/usuarioService';

function Usuarios() {
  const [usuarios, setUsuarios] = useState([]);

  useEffect(() => {
    obtenerUsuarios().then(setUsuarios);
  }, []);

  return (
    <div>
      {usuarios.map(usuario => (
        <div key={usuario.id}>
          {usuario.nombre} - {usuario.email}
        </div>
      ))}
    </div>
  );
}

export default Usuarios;