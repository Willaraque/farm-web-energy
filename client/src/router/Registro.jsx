import React from 'react';
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../Autenticacion/AuthProvider";
import NavbarFijo from "../components/NavbarFijo";
import { Navigate } from "react-router-dom";
import { createUser } from "../api/Users";

function Registro() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [surname, setSurname] = useState("");
    const [tel, setTel] = useState("");
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

        createUser({ name, username, password, surname, tel })
            .then(response => {
                console.log(response)
                setIsSubmitting(false);
                alert('Usuario creado satisfactoriamente');
                setUsername([username, response.data.username]);
                setPassword([password, response.data.password]);
                navigate('/');
            })
            .catch(error => {
                setIsSubmitting(false);
                let errorMsg = 'Completar los campos';

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
            <div className="flex items-center justify-center h-[calc(100vh-10rem)] mt-20">
                <div className="flex flex-col">
                    <form
                        className="grid items-center bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-8 sm:p-10 shadow-2xl w-full max-w-sm sm:max-w-md text-center"
                        onSubmit={handleSubmit}
                    >
                        <h1 className="flex justify-center text-3xl font-bold my-4">Usuario</h1>

                        <input
                            type="text"
                            placeholder="Nombre"
                            className="block py-2 px-3 mb-2  text-black rounded"
                            onChange={(e) => setName(e.target.value)}
                            value={name}
                            autoFocus
                        />
                        <input
                            type="text"
                            placeholder="Apellido"
                            className="block py-2 px-3 mb-2  text-black rounded"
                            onChange={(e) => setSurname(e.target.value)}
                            value={surname}
                        />
                        <input
                            type="text"
                            placeholder="usuario@wac.com"
                            className="block py-2 px-3 mb-2  text-black rounded"
                            onChange={(e) => setUsername(e.target.value)}
                            value={username}
                        />
                        <input
                            type="password"
                            placeholder="password"
                            className="block py-2 px-3 mb-2  text-black rounded"
                            onChange={(e) => setPassword(e.target.value)}
                            value={password}
                        />
                        <input
                            type="text"
                            placeholder="telf"
                            className="block py-2 px-3 mb-2  text-black rounded"
                            onChange={(e) => setTel(e.target.value)}
                            value={tel}
                        />
                        <button
                            className="w-full py-2 sm:py-3 bg-indigo-500 hover:bg-indigo-600 text-white px-2 font-bold rounded-lg shadow-md transition-all duration-300">
                            Crear Usuario
                        </button>
                        {!!errorResponse && <div className="errorMessage flex justify-center text-red-600 text-lg font-semibold mt-3 bg-opacity-10 py-2 px-4 rounded">{`¡${errorResponse}!`}</div>}
                    </form>
                </div>
            </div>

        </NavbarFijo>

    )
}

export default Registro