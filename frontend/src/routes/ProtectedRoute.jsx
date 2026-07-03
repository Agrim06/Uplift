import React from 'react';
import { Navigate } from 'react-router-dom';
import { getAccessToken } from '../services/api';

export default function ProtectedRoute({ children }) {
  const token = getAccessToken();

  if (!token) {
    console.warn("No token found. Redirecting to Home.");
    return <Navigate to="/" replace />;
  }

  return children;
}
