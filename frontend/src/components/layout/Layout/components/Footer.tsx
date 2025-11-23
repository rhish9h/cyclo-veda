/**
 * Footer Component
 * 
 * Simple footer component for all authenticated pages.
 * Contains copyright information and app version.
 */

import React from 'react';
import styles from '../Layout.module.css';

/**
 * Footer component with app information
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const appVersion = '1.0.0'; // TODO: Get from package.json or environment

  return (
    <footer className={styles.layoutFooter}>
      <div className={styles.footerContent}>
        <p className={styles.footerText}>
          © {currentYear} Cyclo Veda. All rights reserved.
        </p>
        <p className={styles.footerVersion}>
          Version {appVersion}
        </p>
      </div>
    </footer>
  );
};

export default Footer;