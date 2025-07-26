import type { LoginCredentials, AuthResponse, User } from '../types/auth';
import { API_BASE_URL, API_ENDPOINTS, STORAGE_KEYS } from '../constants';
import { ApiError, errorHandler } from '../utils/errorHandler';
import { storage } from '../utils';

/**
 * Authentication service for handling user authentication operations
 * Implements singleton pattern for consistent state management
 */
class AuthService {
  private static instance: AuthService;

  private constructor() {}

  /**
   * Get singleton instance of AuthService
   */
  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * Authenticate user with email and password
   * @param credentials - User login credentials
   * @returns Promise resolving to authentication response
   * @throws ApiError on authentication failure
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || 'Invalid credentials',
          response.status,
          'LOGIN_FAILED'
        );
      }

      const data: AuthResponse = await response.json();
      this.setToken(data.access_token);

      return data;
    } catch (error) {
      const handledError = errorHandler.handleApiError(error);
      errorHandler.logError(handledError, 'AuthService.login');
      throw handledError;
    }
  }

  /**
   * Get current authenticated user information
   * @returns Promise resolving to user data
   * @throws ApiError if not authenticated or request fails
   */
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    if (!token) {
      throw new ApiError('No authentication token found', 401, 'NO_TOKEN');
    }

    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.AUTH.ME}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.logout(); // Clear invalid token
        }

        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || 'Failed to get user information',
          response.status,
          'GET_USER_FAILED'
        );
      }

      return await response.json();
    } catch (error) {
      const handledError = errorHandler.handleApiError(error);
      errorHandler.logError(handledError, 'AuthService.getCurrentUser');
      throw handledError;
    }
  }

  /**
   * Log out current user and clear authentication data
   */
  logout(): void {
    try {
      storage.remove(STORAGE_KEYS.ACCESS_TOKEN);
      storage.remove(STORAGE_KEYS.USER_DATA);
    } catch (error) {
      errorHandler.logError(error as Error, 'AuthService.logout');
    }
  }

  /**
   * Get stored authentication token
   * @returns Token string or null if not found
   */
  getToken(): string | null {
    return storage.get(STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Store authentication token securely
   * @param token - JWT token to store
   */
  private setToken(token: string): void {
    storage.set(STORAGE_KEYS.ACCESS_TOKEN, token);
  }

  /**
   * Check if user is currently authenticated
   * @returns True if user has valid token
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      // Basic token validation (check if it's not expired)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      // If token parsing fails, consider it invalid
      this.logout();
      return false;
    }
  }

  /**
   * Refresh authentication token if needed
   * This is a placeholder for future implementation
   */
  async refreshToken(): Promise<void> {
    // TODO: Implement token refresh logic when backend supports it
    throw new Error('Token refresh not implemented yet');
  }
}

export default AuthService.getInstance();
