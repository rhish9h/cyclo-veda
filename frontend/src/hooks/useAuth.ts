import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { ROUTES } from '../constants';
import { errorHandler } from '../utils/errorHandler';
import type { LoginCredentials, User } from '../types/auth';

/**
 * Authentication hook for managing user authentication state
 * Provides login, logout, and authentication status management
 */
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  /**
   * Clear authentication state
   */
  const clearAuthState = useCallback(() => {
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  }, []);

  /**
   * Set authentication state for successful login
   */
  const setAuthState = useCallback((userData: User) => {
    setUser(userData);
    setIsAuthenticated(true);
    setError(null);
  }, []);

  /**
   * Initialize authentication state on component mount
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser();
          setAuthState(userData);
        } else {
          clearAuthState();
        }
      } catch (error) {
        // Token might be expired or invalid
        const handledError = errorHandler.handleApiError(error);
        errorHandler.logError(handledError, 'useAuth.initializeAuth');

        authService.logout();
        clearAuthState();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [setAuthState, clearAuthState]);

  /**
   * Login user with credentials
   * @param credentials - User login credentials
   * @throws Error if login fails
   */
  const login = useCallback(
    async (credentials: LoginCredentials): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        await authService.login(credentials);
        const userData = await authService.getCurrentUser();
        setAuthState(userData);
        navigate(ROUTES.DASHBOARD);
      } catch (error) {
        const handledError = errorHandler.handleApiError(error);
        const displayMessage = errorHandler.getDisplayMessage(handledError);

        errorHandler.logError(handledError, 'useAuth.login');
        clearAuthState();
        setError(displayMessage);

        throw handledError;
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, setAuthState, clearAuthState]
  );

  /**
   * Logout current user and redirect to login page
   */
  const logout = useCallback((): void => {
    try {
      authService.logout();
      clearAuthState();
      navigate(ROUTES.LOGIN);
    } catch (error) {
      errorHandler.logError(error as Error, 'useAuth.logout');
      // Still clear state and navigate even if logout fails
      clearAuthState();
      navigate(ROUTES.LOGIN);
    }
  }, [navigate, clearAuthState]);

  /**
   * Clear any authentication errors
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    user,
    isLoading,
    isAuthenticated,
    error,

    // Actions
    login,
    logout,
    clearError,
  };
};
