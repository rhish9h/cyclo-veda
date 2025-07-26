/**
 * Protected Route Component
 *
 * A higher-order component that protects routes requiring authentication.
 *
 * Functionality:
 * - Checks user authentication status using authService
 * - Renders child components if user is authenticated
 * - Redirects to login page if user is not authenticated
 * - Uses 'replace' navigation to prevent back button issues
 *
 * Usage:
 * <ProtectedRoute>
 *   <Dashboard />
 * </ProtectedRoute>
 *
 * This component is essential for securing private areas of the application
 * and ensuring only authenticated users can access protected content.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../../services/authService';

/**
 * Props interface for ProtectedRoute component
 */
interface ProtectedRouteProps {
  /** Child components to render if user is authenticated */
  children: React.ReactNode;
}

/**
 * Protected route wrapper component
 * Conditionally renders children based on authentication status
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // Check if user is currently authenticated (has valid token)
  const isAuthenticated = authService.isAuthenticated();

  // Render children if authenticated, otherwise redirect to login
  // Using 'replace' prevents users from navigating back to protected routes
  return isAuthenticated ? <>{children}</> : <Navigate to='/login' replace />;
};

export default ProtectedRoute;
