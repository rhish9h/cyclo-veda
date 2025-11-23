/**
 * Header Component
 * 
 * Shared header component for all authenticated pages.
 * Contains app title, navigation buttons, and logout functionality.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../hooks/useAuth';
import { ROUTES } from '../../../../constants';
import styles from '../Layout.module.css';

interface HeaderProps {
  title?: string;
  showSettings?: boolean;
  showLogout?: boolean;
}

/**
 * Header component with navigation and user actions
 */
const Header: React.FC<HeaderProps> = ({ 
  title = 'Cyclo Veda',
  showSettings = true,
  showLogout = true 
}) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  /**
   * Handles user logout
   */
  const handleLogout = () => {
    logout();
  };

  /**
   * Handles navigation to Settings page
   */
  const handleSettings = () => {
    navigate(ROUTES.SETTINGS);
  };

  return (
    <header className={styles.layoutHeader}>
      <h1 className={styles.layoutHeaderTitle}>{title}</h1>
      <div className={styles.layoutHeaderActions}>
        {showSettings && (
          <button onClick={handleSettings} className={`${styles.layoutHeaderButton} ${styles.settingsButton}`}>
            Settings
          </button>
        )}
        {showLogout && (
          <button onClick={handleLogout} className={`${styles.layoutHeaderButton} ${styles.logoutButton}`}>
            Logout
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;