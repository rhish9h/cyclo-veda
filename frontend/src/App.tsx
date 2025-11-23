/**
 * Main App Component
 * Sets up routing, lazy loading, and provides the main application structure
 */

import { Suspense, lazy } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ROUTES } from './constants';
import { ErrorBoundary } from './components/ErrorBoundary';
import ProtectedRoute from './components/auth/ProtectedRoute';
import PublicRoute from './components/auth/PublicRoute';
import './App.css';

// Lazy load components for better performance
const Login = lazy(() => import('./components/auth/Login'));
const Dashboard = lazy(() => import('./components/layout/Dashboard/Dashboard'));
const Settings = lazy(() => import('./components/layout/Settings/Settings'));

/**
 * Loading component displayed during lazy loading
 */
const LoadingSpinner = () => (
  <div className='min-h-screen flex items-center justify-center bg-gray-50'>
    <div className='flex flex-col items-center space-y-4'>
      <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600'></div>
      <p className='text-gray-600'>Loading...</p>
    </div>
  </div>
);

/**
 * Route-specific error boundary component
 */
const RouteErrorBoundary = ({ children }: { children: React.ReactNode }) => (
  <ErrorBoundary
    fallback={
      <div className='min-h-screen flex items-center justify-center bg-gray-50'>
        <div className='max-w-md w-full bg-white shadow-lg rounded-lg p-6 text-center'>
          <h2 className='text-lg font-semibold text-gray-900 mb-2'>
            Page Error
          </h2>
          <p className='text-gray-600 mb-4'>
            This page encountered an error. Please try navigating to a different
            page.
          </p>
          <button
            onClick={() => (window.location.href = ROUTES.HOME)}
            className='bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors'
          >
            Go Home
          </button>
        </div>
      </div>
    }
  >
    {children}
  </ErrorBoundary>
);

/**
 * Main App component with routing, lazy loading, and error boundaries
 * Follows React Vite best practices for performance and maintainability
 */
function App() {
  return (
    <Router>
      <div className='App'>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Public Routes */}
            <Route
              path={ROUTES.LOGIN}
              element={
                <RouteErrorBoundary>
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                </RouteErrorBoundary>
              }
            />

            {/* Protected Routes */}
            <Route
              path={ROUTES.DASHBOARD}
              element={
                <RouteErrorBoundary>
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                </RouteErrorBoundary>
              }
            />

            <Route
              path={ROUTES.SETTINGS}
              element={
                <RouteErrorBoundary>
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                </RouteErrorBoundary>
              }
            />

            {/* Default and Fallback Routes */}
            <Route
              path={ROUTES.HOME}
              element={<Navigate to={ROUTES.DASHBOARD} replace />}
            />
            <Route path='*' element={<Navigate to={ROUTES.LOGIN} replace />} />
          </Routes>
        </Suspense>
      </div>
    </Router>
  );
}

export default App;
