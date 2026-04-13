import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function FullPageSpinner() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-900">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-600 border-t-blue-400" />
    </div>
  );
}

export default function ProtectedRoute() {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <FullPageSpinner />;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return <Outlet />;
}
