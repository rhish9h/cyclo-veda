/**
 * Authentication Type Definitions
 *
 * This file contains all TypeScript interfaces and types related to authentication
 * in the Cyclo Veda application. These types ensure type safety across the entire
 * authentication system and provide clear contracts for API interactions.
 */

/**
 * Login credentials interface
 * Used for user authentication requests
 */
export interface LoginCredentials {
  /** User's email address (used as username) */
  email: string;
  /** User's password */
  password: string;
}

/**
 * Authentication response interface
 * Represents the response from the login API endpoint
 */
export interface AuthResponse {
  /** JWT access token for authenticated requests */
  access_token: string;
  /** Type of token (typically 'bearer') */
  token_type: string;
}

/**
 * User profile interface
 * Represents the authenticated user's information
 */
export interface User {
  /** User's email address */
  email: string;
  /** Whether the user account is active */
  is_active: boolean;
}

/**
 * Authentication context interface
 * Defines the shape of the authentication context used throughout the app
 * This interface ensures consistent access to auth state and methods
 */
export interface AuthContextType {
  /** Current authenticated user (null if not authenticated) */
  user: User | null;
  /** Function to authenticate user with credentials */
  login: (credentials: LoginCredentials) => Promise<void>;
  /** Function to log out current user */
  logout: () => void;
  /** Loading state during authentication operations */
  isLoading: boolean;
  /** Whether user is currently authenticated */
  isAuthenticated: boolean;
}
