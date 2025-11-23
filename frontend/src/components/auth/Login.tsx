/**
 * Login Component
 *
 * Provides user authentication interface for the Cyclo Veda application.
 * Features:
 * - Email/password form validation
 * - Real-time error handling and display
 * - Loading states during authentication
 * - Responsive design with modern UI
 * - Integration with centralized auth system
 *
 * Test Credentials:
 * - admin@cycloveda.com / password
 * - user@example.com / password
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { LoginCredentials } from '../../types/auth';
import styles from './Login.module.css';

/**
 * Login form component with authentication handling
 * Manages form state, validation, and user authentication flow
 */
const Login: React.FC = () => {
  // Form state management
  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });

  // Error state for displaying authentication failures
  const [error, setError] = useState('');

  // Authentication hook for login functionality and loading state
  const { login, isLoading } = useAuth();

  // Navigation hook for programmatic routing
  const navigate = useNavigate();

  /**
   * Handles input field changes and updates form state
   * Clears any existing errors when user starts typing for better UX
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing to provide immediate feedback
    if (error) setError('');
  };

  /**
   * Handles form submission and user authentication
   * Prevents default form submission, calls auth service, and handles errors
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear any previous errors

    try {
      // Attempt login using the auth hook (handles token storage and navigation)
      await login(formData);
      // Navigation is handled automatically by the useAuth hook on success
    } catch (err) {
      // Display user-friendly error message
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginCard}>
        {/* Login form header with branding and instructions */}
        <div className={styles.loginHeader}>
          <h1>Welcome to Cyclo Veda</h1>
          <p>Sign in to your account</p>
        </div>

        {/* Main login form with email/password fields */}
        <form onSubmit={handleSubmit} className={styles.loginForm}>
          {/* Email input field */}
          <div className={styles.formGroup}>
            <label htmlFor='email'>Email</label>
            <input
              type='email'
              id='email'
              name='email'
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder='Enter your email'
              disabled={isLoading} // Prevent input during authentication
            />
          </div>

          {/* Password input field */}
          <div className={styles.formGroup}>
            <label htmlFor='password'>Password</label>
            <input
              type='password'
              id='password'
              name='password'
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder='Enter your password'
              disabled={isLoading} // Prevent input during authentication
            />
          </div>

          {/* Error message display - only shown when there's an error */}
          {error && <div className={styles.errorMessage}>{error}</div>}

          {/* Submit button with loading state */}
          <button type='submit' className={styles.loginButton} disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Footer with registration link (placeholder for future feature) */}
        <div className={styles.loginFooter}>
          <p>
            Don't have an account?
            <button
              type='button'
              className={styles.linkButton}
              onClick={() => navigate('/register')} // TODO: Implement registration page
            >
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
