// src/components/Reserva.js
import React from 'react';

const Reserva = ({ reserva }) => (
  <li>
    <h2>Reserva {reserva.id}</h2>
    <p>Fecha: {reserva.fecha}</p>
    <p>Hora: {reserva.hora}</p>
    <p>Estado: {reserva.estado}</p>
    <p>Detalle: {reserva.detalle}</p>
  </li>
);

export default Reserva;
