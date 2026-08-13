import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/auth-context";

export default function ProtectedRoute() {
  const auth = useAuth();
  const location = useLocation();
  return auth.isAutenticated ? (
    <Outlet />
  ) : (
    <Navigate to="/" replace state={{ from: location }} />
  );
}
