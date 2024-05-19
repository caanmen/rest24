// src/pages/Mesas.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Mesa from '../components/Mesa';

const Mesas = () => {
  const [mesas, setMesas] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:3300/mesas')
      .then(response => setMesas(response.data))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      <h1>Mesas</h1>
      <ul>
        {mesas.map(mesa => (
          <Mesa key={mesa.numero_mesa} mesa={mesa} />
        ))}
      </ul>
    </div>
  );
};

export default Mesas;
