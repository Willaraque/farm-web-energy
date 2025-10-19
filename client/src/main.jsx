import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Dashboard from "./router/Dashboard.jsx";
import Login from "./router/Login.jsx";
import Registro from "./router/Registro.jsx";
import ProtectedRouter from "./router/ProtectedRouter.jsx";
import AuthProvider from "./Autenticacion/AuthProvider.jsx";
import LisTask from "./pages/LisTask.jsx";
import TaskForm from "./pages/TaskForm.jsx";
import PreciosForm from "./pages/TablePrices.jsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Login />
  },
  {
    path: "/registro",
    element: <Registro />
  },
  {
    path: "/",
    element: <ProtectedRouter />,
    children: [{
      path: "/dashboard",
      element: <Dashboard />
    }]
  },
  {
    path: "/",
    element: <ProtectedRouter />,
    children: [{
      path: "/productos",
      element: <LisTask />
    }]
  },
  {
    path: "/",
    element: <ProtectedRouter />,
    children: [{
      path: "/productos/:id",
      element: <TaskForm />
    }]
  },
  {
    path: "/",
    element: <ProtectedRouter />,
    children: [{
      path: "/productos/create",
      element: <TaskForm />
    }]
  },
  {
    path: "/",
    element: <ProtectedRouter />,
    children: [{
      path: "/precios",
      element: <PreciosForm />
    }]
  }
]);


{/* <App /> */}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
      <AuthProvider>
        <RouterProvider router={router}/>
      </AuthProvider>
  </React.StrictMode>
);
