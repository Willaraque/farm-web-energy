import React from 'react';
import { useState, useEffect } from "react";
import NavbarFijo from "../components/NavbarFijo";
import { useAuth } from "../Autenticacion/AuthProvider";
import { Navigate, useNavigate } from "react-router-dom";
import { AccessToken } from "../api/Tokens";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorResponse, setErrorResponse] = useState("");

    const [isSubmitting, setIsSubmitting] = useState(false);
    const auth = useAuth();
    const navigate = useNavigate();



    // Función para manejar el envío del formulario
    const handleSubmit = (e) => {
        e.preventDefault();

        if (isSubmitting) return;
        setIsSubmitting(true);
        setErrorResponse(''); // Limpia errores previos

        AccessToken(username, password)
            .then(response => {
                setIsSubmitting(false);
                if (response.data.access_token) {
                    auth.saveUser(response)
                    navigate('/dashboard')
                }
            })
            .catch(error => {
                setIsSubmitting(false);
                let errorMsg = '¡Usuario Invalido!';

                if (error.response && error.response.status === 400) {
                    // Si hay un mensaje de error específico en la respuesta, úsalo
                    if (error.response.data && error.response.data.detail) {
                        errorMsg = error.response.data.detail;
                    }
                }
                // Setea el mensaje de error sin concatenar
                setErrorResponse(errorMsg);
                e.target.reset(); // Resetea el formulario si hay error
            });
    };

    if (auth.isAutenticated) {
        return <Navigate to='/dashboard' />;
    }

    // Efecto para limpiar el mensaje de error después de 10 segundos
    useEffect(() => {
        if (errorResponse) {
            const timer = setTimeout(() => {
                setErrorResponse("");  // Limpiamos el mensaje de error
            }, 5000);  // 5 segundos (10000 milisegundos)

            return () => clearTimeout(timer);  // Limpiar el timeout si el componente se desmonta
        }
    }, [errorResponse]);

    return (
        <NavbarFijo>
            <div className="flex items-center mt-2 justify-center min-h-screen bg-cover bg-center px-4 sm:px-6">
                <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-8 sm:p-10 shadow-2xl w-full max-w-sm sm:max-w-md text-center">
                    {/* Aquí añadimos el nombre o logo de WAC */}
                    <div className="mb-6">
                        <img src="/src/assets/favicon-256x256.png" alt="WAC Logo" className="mx-auto w-24 h-24 mb-4 shadow-md" /> {/* Si prefieres usar el logo */}
                    </div>
                    <h1 className="text-white text-3xl sm:text-4xl font-bold mb-4 sm:mb-6">Login</h1>
                    <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="usuario@wac.com"
                                className="w-full py-2 sm:py-3 px-4 text-black rounded-lg shadow-md border border-gray-300 focus:ring-2 focus:ring-indigo-600 focus:outline-none"
                                onChange={(e) => setUsername(e.target.value)}
                                value={username}
                                autoFocus
                            />
                        </div>
                        <div className="relative">
                            <input
                                type="password"
                                placeholder="password"
                                className="w-full py-2 sm:py-3 px-4 text-black rounded-lg shadow-md border border-gray-300 focus:ring-2 focus:ring-indigo-600 focus:outline-none"
                                onChange={(e) => setPassword(e.target.value)}
                                value={password}
                            />
                        </div>
                        <button
                            type="submit"
                            className={`w-full py-2 sm:py-3 bg-indigo-500 hover:bg-indigo-600 text-white font-bold rounded-lg shadow-md transition-all duration-300 ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Iniciando...' : 'Iniciar Sesión'}
                        </button>
                        {!!errorResponse && (
                            <div className="errorMessage flex justify-center text-red-600 text-lg font-semibold mt-3 bg-opacity-10 py-2 px-4 rounded">
                                {`${errorResponse}!`}
                            </div>
                        )}
                    </form>
                    <div className="text-white mt-4 sm:mt-6">
                        <a href="/forgot-password" className="hover:underline">¿Olvidaste tu contraseña?</a> |
                        <a href="/registro" className="hover:underline ml-2">Registro</a>
                    </div>
                </div>
            </div>

        </NavbarFijo>

    )
}

export default Login