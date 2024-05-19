// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Inicio from './pages/Inicio';
import Mesas from './pages/Mesas';
import Reservas from './pages/Reservas';
import Usuarios from './pages/Usuarios';
import Login from './pages/Login';
import Register from './pages/Register';
import PrivateRoute from './components/PrivateRoute';
import { AuthProvider, useAuth } from './context/AuthContext';

const PrivateRouteWrapper = ({ element: Element, ...rest }) => {
  const { user } = useAuth();
  return user ? <Element {...rest} /> : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<Inicio />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/mesas" element={<PrivateRouteWrapper element={Mesas} />} />
              <Route path="/reservas" element={<PrivateRouteWrapper element={Reservas} />} />
              <Route path="/usuarios" element={<PrivateRouteWrapper element={Usuarios} />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
