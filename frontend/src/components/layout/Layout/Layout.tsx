/**
 * Layout Component
 * 
 * Main layout wrapper for all authenticated pages.
 * Provides consistent structure with header, sidebar, content area, and footer.
 */

import Header from './components/Header';
import Footer from './components/Footer';
import styles from './Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showHeader?: boolean;
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
  showFooter = true,
  headerProps = {}
}) => {

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
      
      {/* Main content area */}
      <div className={styles.layoutMain}>
        
        {/* Page content */}
        <main className={`${styles.layoutContent}`}>
          {children}
        </main>
      </div>
      
      {/* Footer */}
      {showFooter && <Footer />}
    </div>
  );
};

export default Layout;