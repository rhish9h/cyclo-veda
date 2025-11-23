/**
 * Sidebar Component
 * 
 * Navigation sidebar for authenticated pages.
 * Contains main navigation links and highlights the active route.
 */

import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ROUTES } from '../../../../constants';
import styles from '../Layout.module.css';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

/**
 * Navigation sidebar with menu items
 */
const Sidebar: React.FC<SidebarProps> = ({ 
  isOpen = true, 
  onClose 
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  /**
   * Navigation menu items configuration
   */
  const navItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      path: ROUTES.DASHBOARD,
      description: 'Overview and analytics'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      path: ROUTES.SETTINGS,
      description: 'Account and app preferences'
    }
  ];

  /**
   * Handle navigation to a specific route
   */
  const handleNavigation = (path: string) => {
    navigate(path);
    // Close sidebar on mobile after navigation
    if (onClose && window.innerWidth <= 768) {
      onClose();
    }
  };

  /**
   * Check if a navigation item is currently active
   */
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <aside className={`${styles.layoutSidebar} ${isOpen ? '' : styles.closed}`}>
      <nav className={styles.sidebarNav}>
        <ul className={styles.navList}>
          {navItems.map((item) => (
            <li key={item.id} className={styles.navItem}>
              <button
                className={`${styles.navButton} ${isActive(item.path) ? styles.active : ''}`}
                onClick={() => handleNavigation(item.path)}
                aria-label={`Navigate to ${item.label}`}
              >
                <span className={styles.navIcon}>{item.icon}</span>
                <span className={styles.navText}>
                  <span className={styles.navLabel}>{item.label}</span>
                  <span className={styles.navDescription}>{item.description}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;