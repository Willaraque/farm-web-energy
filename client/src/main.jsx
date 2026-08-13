import React, { lazy, Suspense } from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import "./index.css";
import AuthProvider from "./features/auth/AuthProvider";
import ProtectedRoute from "./routes/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PhoneAuthPage from "./pages/PhoneAuthPage";
import OAuthCallbackPage from "./pages/OAuthCallbackPage";
import SpinnerLoader from "./components/SpinnerLoader";
import ThemeProvider from "./features/theme/ThemeProvider";

const DashboardPage = lazy(() => import("./features/dashboard/DashboardPage"));
const ProductsPage = lazy(() => import("./features/products/ProductsPage"));
const ProductFormPage = lazy(() => import("./features/products/ProductFormPage"));
const MarketPricesPage = lazy(() => import("./features/market/MarketPricesPage"));
const deferred = (element) => <Suspense fallback={<SpinnerLoader label="Cargando pantalla" />}>{element}</Suspense>;

const router = createBrowserRouter([
  { path: "/", element: <LoginPage /> },
  { path: "/registro", element: <RegisterPage /> },
  { path: "/recuperar", element: <PhoneAuthPage /> },
  { path: "/auth/callback", element: <OAuthCallbackPage /> },
  { element: <ProtectedRoute />, children: [
    { path: "/dashboard", element: deferred(<DashboardPage />) },
    { path: "/productos", element: deferred(<ProductsPage />) },
    { path: "/productos/create", element: deferred(<ProductFormPage />) },
    { path: "/productos/:id", element: deferred(<ProductFormPage />) },
    { path: "/precios", element: deferred(<MarketPricesPage />) },
  ] },
  { path: "*", element: <Navigate to="/" replace /> },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode><ThemeProvider><AuthProvider><RouterProvider router={router} future={{ v7_startTransition: true }} /></AuthProvider></ThemeProvider></React.StrictMode>,
);
