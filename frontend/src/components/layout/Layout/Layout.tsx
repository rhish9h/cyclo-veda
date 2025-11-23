/**
 * Layout Component
 * 
 * Main layout wrapper for all authenticated pages.
 * Provides consistent structure with header, sidebar, content area, and footer.
 */

import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import styles from './Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showHeader?: boolean;
  showSidebar?: boolean;
  showFooter?: boolean;
  headerProps?: {
    showSettings?: boolean;
    showLogout?: boolean;
  };
}

/**
 * Layout component that wraps authenticated pages
 */
const Layout: React.FC<LayoutProps> = ({
  children,
  title = 'Cyclo Veda',
  showHeader = true,
  showSidebar = true,
  showFooter = true,
  headerProps = {}
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  /**
   * Toggle sidebar visibility
   */
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  /**
   * Close sidebar (for mobile)
   */
  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className={styles.layoutContainer}>
      {/* Header */}
      {showHeader && (
        <Header 
          title={title}
          showSettings={headerProps.showSettings}
          showLogout={headerProps.showLogout}
        />
      )}
      
      {/* Main content area with sidebar */}
      <div className={styles.layoutMain}>
        {/* Sidebar */}
        {showSidebar && (
          <Sidebar 
            isOpen={sidebarOpen}
            onClose={closeSidebar}
          />
        )}
        
        {/* Page content */}
        <main className={`${styles.layoutContent} ${showSidebar ? styles.withSidebar : styles.fullWidth}`}>
          {/* Mobile menu toggle */}
          {showSidebar && (
            <button 
              className={styles.sidebarToggle}
              onClick={toggleSidebar}
              aria-label='Toggle sidebar'
            >
              ☰
            </button>
          )}
          
          {children}
        </main>
      </div>
      
      {/* Footer */}
      {showFooter && <Footer />}
    </div>
  );
};

export default Layout;