import React from 'react';
import { Children } from "react";
import PropTypes from 'prop-types';
import { Link } from "react-router-dom";

function NavbarFijo({ children }) {
    return (
        <>
            <header className="fixed top-0 w-full bg-opacity-20 backdrop-blur-lg py-4 shadow-lg z-10 border-b border-indigo-600">
                <nav className="max-w-7xl mx-auto px-4">
                    <ul className="flex justify-between items-center text-2xl sm:text-3xl font-bold text-white">
                        <li>
                            <Link to="/" className="hover:text-indigo-300 transition-colors duration-300 hover:underline">
                                Inicio
                            </Link>
                        </li>
                        <li>
                            <Link to="/registro" className="hover:text-indigo-300 transition-colors duration-300 hover:underline">
                                Registro
                            </Link>
                        </li>
                    </ul>
                </nav>
            </header>
            <main>
                {children}
            </main>
        </>

    )
}

NavbarFijo.propTypes = {
    children: PropTypes.node.isRequired
};

export default NavbarFijo