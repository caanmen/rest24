// src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => (
  <header>
    <nav>
      <ul>
        <li><Link to="/">Inicio</Link></li>
        <li><Link to="/mesas">Mesas</Link></li>
        <li><Link to="/reservas">Reservas</Link></li>
        <li><Link to="/usuarios">Usuarios</Link></li>
      </ul>
    </nav>
  </header>
);

export default Header;
