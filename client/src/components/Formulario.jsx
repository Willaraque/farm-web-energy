import React from 'react';
import { useState, useEffect } from "react";

function Formulario({setUser}) {
  const [usuario, setUsuario] = useState("");
  const [contraseña, setContraseña] = useState("");
  const [error, setError] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (usuario == "" || contraseña == "") {
      setError(true);
      return;
    }

    setError(false);

    setUser([usuario])
  };

  return (
    <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
      <div className="flex flex-col">
        <form
          className="grid items-center bg-violet-600 p-10 rounded"
          onSubmit={handleSubmit}
        >
          <h1 className="flex justify-center text-3xl font-bold my-4">Login</h1>
          <input
            type="text"
            placeholder="usuario@wac.com"
            className="block py-2 px-3 mb-2  text-black rounded"
            onChange={(e) => setUsuario(e.target.value)}
            value={usuario}
            autoFocus
          />
          <input
            type="password"
            placeholder="Password"
            className="block py-2 px-3 mb-2  text-black rounded"
            onChange={(e) => setContraseña(e.target.value)}
            value={contraseña}
          />
          <button 
            className="bg-violet-200 hover:bg-white text-slate-800 py-2 px-2 rounded ">
            Iniciar Sesion
          </button>
        </form>

        {error && (
          <p className="flex justify-center text-red-400 text-xl font-bold my-2">
            Todos los campos son obligatorios
          </p>
        )}
      </div>
    </div>
  );
}

export default Formulario;
