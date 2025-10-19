import React from 'react';
import { useState } from 'react'
import PropTypes from 'prop-types';
import { deleteToken } from '../api/Tokens';
import { useAuth } from '../Autenticacion/AuthProvider';
import { Link } from 'react-router-dom';
import '../EstilosCSS/navbar.css'
import '../EstilosCSS/Sidebar.css'; // Importa los estilos que definirás a continuación


function LogingOut({ children }) {

    const auth = useAuth();
    const [isOpen, setIsOpen] = useState(false);


    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    const handleSignOut = async (e) => {
        e.preventDefault();

        try {
            const _id = auth.getIdMongo();
            const response = await deleteToken(_id);
            if (response.data.valid) {
                auth.signOuth();
            }
        } catch (error) {
            console.log('Error al cerrar sesion con el usuario', error)
        }

    }

    return (
        <>
            <div style={navbarStyle}>
                {/* <div className="container"> */}
                <div style={{display:'flex', flexDirection:'row', justifyContent:'center', alignItems:'center'} }>
                        <img src="/src/assets/favicon-32x32.png" alt="Logo" style={{ height: '40px', marginRight: '10px' }} />
                        <h1 className="text-xl font-sans text-white">{`Usuario: ${auth.getUser()}` || ""}</h1>
                    </div>
                    <button
                        className="block lg:hidden mt-4 focus:outline-none"
                        onClick={toggleSidebar}
                        style={{ color: isOpen ? 'red' : 'fuchsia' }}
                    >
                        {isOpen ? 'X' : '☰'}
                    </button>
                    <nav
                        className={`w-full  ${isOpen ? 'block' : 'hidden'} lg:flex lg:items-center lg:w-auto`}
                    >
                        <ul className="lg:flex lg:space-x-6 text-center">
                            <li className="nav-item">
                                <Link to="/dashboard" className="block lg:inline-block p-2">
                                    Inicio
                                </Link>
                            </li>
                            <li className="nav-item">
                                <Link to="/precios" className="block lg:inline-block p-2">
                                    Precios
                                </Link>
                            </li>
                            <li className="nav-item">
                                <Link to="/productos" className="block lg:inline-block p-2">
                                    Productos
                                </Link>
                            </li>
                            <li className="nav-item">
                                <Link to="/productos/create" className="block lg:inline-block p-2">
                                    Crear Productos
                                </Link>
                            </li>
                            <li className="nav-item">
                                <a href="#" onClick={handleSignOut} className="block lg:inline-block p-2">
                                    Cerrar Sesión
                                </a>
                            </li>
                        </ul>
                    </nav>
            </div>
            <main>{children}</main>

        </>
    )
};

LogingOut.propTypes = {
    children: PropTypes.node.isRequired
};


export default LogingOut

const navbarStyle = {
    background: "linear-gradient(90deg, #4b0082, #800080)", // Gradiente llamativo
    flexDirection: window.innerWidth > 768 ? "row" : "column",
    color: "white",
    padding: "10px 20px",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.2)", // Sombra para profundidad
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    // position: "fixed", // Fijo en la parte superior
    width: "100%",
    // zIndex: 1000, // Por encima de otros elementos
  };