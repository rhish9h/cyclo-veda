/**
 * Public Route Component
 *
 * A higher-order component that handles routes accessible only to unauthenticated users.
 *
 * Functionality:
 * - Checks user authentication status using authService
 * - Renders child components if user is NOT authenticated
 * - Redirects to dashboard if user is already authenticated
 * - Prevents authenticated users from accessing login/register pages
 * - Uses 'replace' navigation to prevent back button issues
 *
 * Usage:
 * <PublicRoute>
 *   <Login />
 * </PublicRoute>
 *
 * This component prevents authenticated users from seeing login forms
 * and automatically redirects them to the main application.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../../services/authService';

/**
 * Props interface for PublicRoute component
 */
interface PublicRouteProps {
  /** Child components to render if user is NOT authenticated */
  children: React.ReactNode;
}

/**
 * Public route wrapper component
 * Conditionally renders children based on authentication status (opposite of ProtectedRoute)
 */
const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  // Check if user is currently authenticated (has valid token)
  const isAuthenticated = authService.isAuthenticated();

  // Render children if NOT authenticated, otherwise redirect to dashboard
  // This prevents authenticated users from accessing login/register pages
  return !isAuthenticated ? (
    <>{children}</>
  ) : (
    <Navigate to='/dashboard' replace />
  );
};

export default PublicRoute;
