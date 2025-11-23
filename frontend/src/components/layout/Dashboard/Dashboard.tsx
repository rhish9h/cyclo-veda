/**
 * Dashboard Component
 *
 * Main application dashboard displayed after successful authentication.
 *
 * Features:
 * - Welcome message and user information display
 * - Fetches and displays data from protected backend endpoints
 * - Loading states and error handling
 * - Logout functionality
 * - Responsive design with modern UI
 *
 * This component serves as the main landing page for authenticated users
 * and demonstrates integration with protected backend APIs.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
// import { API_BASE_URL } from '../../../constants';
import { ROUTES } from '../../../constants';
import './Dashboard.css';

/**
 * Dashboard component for authenticated users
 * Displays welcome message and fetches data from protected endpoints
 */
const Dashboard: React.FC = () => {
  // Component state for API data and UI states
  const [message, setMessage] = useState(''); // Message from backend API
  const [loading, setLoading] = useState(true); // Loading state for API calls
  const [error, setError] = useState(''); // Error state for failed API calls

  // Authentication context for user data and logout functionality
  const { user, logout } = useAuth();

  const navigate = useNavigate();

  /**
   * Effect hook to fetch data from protected backend endpoint on component mount
   * Demonstrates integration with authenticated API calls
   */
  useEffect(() => {
    const fetchData = async () => {
      try {
        setMessage("Ready to Ride?");
      } catch (err) {
        // Handle and display errors
        setError(err instanceof Error ? err.message : 'An error occurred');
        console.error('Error fetching data:', err);
      } finally {
        // Always set loading to false when request completes
        setLoading(false);
      }
    };

    // Fetch data when component mounts
    fetchData();
  }, []);

  /**
   * Handles user logout
   * Calls the logout function from auth context which clears tokens and redirects
   */
  const handleLogout = () => {
    logout();
  };

  /**
   * Handles navigation to Settings page
   */
  const handleSettings = () => {
    navigate(ROUTES.SETTINGS);
  }

  return (
    <div className='dashboard'>
      {/* Dashboard header with title and logout button */}
      <header className='dashboard-header'>
        <h1>Cyclo Veda Dashboard</h1>
        <button onClick={handleSettings} className='settings-button'>
          Settings
        </button>
        <button onClick={handleLogout} className='logout-button'>
          Logout
        </button>
      </header>

      {/* Main dashboard content area */}
      <main className='dashboard-content'>
        <div className='welcome-card'>
          <h2>Welcome back{user?.email ? `, ${user.email}` : ''}!</h2>

          {/* Conditional rendering based on loading/error/success states */}
          {loading ? (
            <p>Loading...</p>
          ) : error ? (
            <p className='error'>Error: {error}</p>
          ) : (
            <p>{message}</p>
          )}
        </div>

        {/* TODO: Add more dashboard widgets and functionality here */}
        {/* Examples: Recent activity, statistics, quick actions, etc. */}
      </main>
    </div>
  );
};

export default Dashboard;
