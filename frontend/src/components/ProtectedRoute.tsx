import type { PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

import { useAuth, type UserRole } from "../auth/AuthContext";

interface ProtectedRouteProps extends PropsWithChildren {
  allowedRole?: UserRole;
}

export function ProtectedRoute({
  allowedRole,
  children,
}: ProtectedRouteProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && user.role !== allowedRole) {
    return (
      <Navigate
        to={user.role === "admin" ? "/admin" : "/study"}
        replace
      />
    );
  }

  return children;
}
