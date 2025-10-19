import React from 'react';
import { Outlet, Navigate } from "react-router-dom"
import { useAuth } from "../Autenticacion/AuthProvider"

function ProtectedRouter() {
    const auth = useAuth();
    return (
        <div>
            {
                auth.isAutenticated ? (<Outlet />) : (
                    <Navigate to='/' />)
            }
        </div>

    )
}

export default ProtectedRouter