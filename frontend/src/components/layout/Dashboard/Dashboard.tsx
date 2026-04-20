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

import React from 'react';
import { useAuth } from '../../../hooks/useAuth';
import Layout from '../Layout/Layout';
import styles from './Dashboard.module.css';

/**
 * Dashboard component for authenticated users
 * Displays welcome message and fetches data from protected endpoints
 */
const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const message = 'Ready to Ride?';

  return (
    <Layout title='Cyclo Veda Dashboard'>
      {/* Main dashboard content area */}
      <div className={styles.dashboardContent}>
        <div className={styles.welcomeCard}>
          <h2>Welcome back{user?.email ? `, ${user.email}` : ''}!</h2>

              <p>{message}</p>
        </div>

        {/* TODO: Add more dashboard widgets and functionality here */}
        {/* Examples: Recent activity, statistics, quick actions, etc. */}
      </div>
    </Layout>
  );
};

export default Dashboard;
