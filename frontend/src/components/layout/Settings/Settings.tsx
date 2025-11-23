/**
 * Settings Component
 * 
 * User settings and account management page.
 * Features multiple sections for profile, security, preferences, and notifications.
 */

import React, { useState } from 'react';
import Layout from '../Layout/Layout';
import styles from './Settings.module.css';

interface SettingsData {
  profile: {
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
  };
  security: {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
  };
  preferences: {
    theme: 'light' | 'dark' | 'system';
    language: string;
    timezone: string;
  };
  notifications: {
    email: boolean;
    push: boolean;
    marketing: boolean;
  };
}

/**
 * Settings component with multiple configuration sections
 */
const Settings: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>('profile');
  const [settingsData, setSettingsData] = useState<SettingsData>({
    profile: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      phone: '+1 (555) 123-4567'
    },
    security: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    },
    preferences: {
      theme: 'light',
      language: 'en',
      timezone: 'America/New_York'
    },
    notifications: {
      email: true,
      push: true,
      marketing: false
    }
  });

  /**
   * Settings navigation sections configuration
   */
  const settingsSections = [
    {
      id: 'profile',
      title: 'Profile',
      icon: '👤',
      description: 'Personal information and account details'
    },
    {
      id: 'security',
      title: 'Security',
      icon: '🔒',
      description: 'Password and authentication settings'
    },
    {
      id: 'preferences',
      title: 'Preferences',
      icon: '⚙️',
      description: 'App appearance and language settings'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      icon: '🔔',
      description: 'Email and push notification preferences'
    }
  ];

  /**
   * Handle input changes in forms
   */
  const handleInputChange = (section: keyof SettingsData, field: string, value: string | boolean) => {
    setSettingsData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  /**
   * Handle form submission
   */
  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving settings:', settingsData);
    alert('Settings saved successfully!');
  };

  /**
   * Render different settings sections
   */
  const renderSectionContent = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <div className={styles.settingsSectionContent}>
            <h3>Profile Information</h3>
            <form className={styles.settingsForm}>
              <div className={styles.formGroup}>
                <label htmlFor='firstName'>First Name</label>
                <input
                  type='text'
                  id='firstName'
                  value={settingsData.profile.firstName}
                  onChange={(e) => handleInputChange('profile', 'firstName', e.target.value)}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='lastName'>Last Name</label>
                <input
                  type='text'
                  id='lastName'
                  value={settingsData.profile.lastName}
                  onChange={(e) => handleInputChange('profile', 'lastName', e.target.value)}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='email'>Email Address</label>
                <input
                  type='email'
                  id='email'
                  value={settingsData.profile.email}
                  onChange={(e) => handleInputChange('profile', 'email', e.target.value)}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='phone'>Phone Number</label>
                <input
                  type='text'
                  id='phone'
                  value={settingsData.profile.phone}
                  onChange={(e) => handleInputChange('profile', 'phone', e.target.value)}
                />
              </div>
              <button type='button' className={styles.saveButton} onClick={handleSave}>
                Save Profile
              </button>
            </form>
          </div>
        );

      case 'security':
        return (
          <div className={styles.settingsSectionContent}>
            <h3>Security Settings</h3>
            <form className={styles.settingsForm}>
              <div className={styles.formGroup}>
                <label htmlFor='currentPassword'>Current Password</label>
                <input
                  type='password'
                  id='currentPassword'
                  value={settingsData.security.currentPassword}
                  onChange={(e) => handleInputChange('security', 'currentPassword', e.target.value)}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='newPassword'>New Password</label>
                <input
                  type='password'
                  id='newPassword'
                  value={settingsData.security.newPassword}
                  onChange={(e) => handleInputChange('security', 'newPassword', e.target.value)}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='confirmPassword'>Confirm New Password</label>
                <input
                  type='password'
                  id='confirmPassword'
                  value={settingsData.security.confirmPassword}
                  onChange={(e) => handleInputChange('security', 'confirmPassword', e.target.value)}
                />
              </div>
              <button type='button' className={styles.saveButton} onClick={handleSave}>
                Update Password
              </button>
            </form>
          </div>
        );

      case 'preferences':
        return (
          <div className={styles.settingsSectionContent}>
            <h3>App Preferences</h3>
            <form className={styles.settingsForm}>
              <div className={styles.formGroup}>
                <label htmlFor='theme'>Theme</label>
                <select
                  id='theme'
                  value={settingsData.preferences.theme}
                  onChange={(e) => handleInputChange('preferences', 'theme', e.target.value)}
                >
                  <option value='light'>Light</option>
                  <option value='dark'>Dark</option>
                  <option value='system'>System</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='language'>Language</label>
                <select
                  id='language'
                  value={settingsData.preferences.language}
                  onChange={(e) => handleInputChange('preferences', 'language', e.target.value)}
                >
                  <option value='en'>English</option>
                  <option value='es'>Spanish</option>
                  <option value='fr'>French</option>
                  <option value='de'>German</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor='timezone'>Timezone</label>
                <select
                  id='timezone'
                  value={settingsData.preferences.timezone}
                  onChange={(e) => handleInputChange('preferences', 'timezone', e.target.value)}
                >
                  <option value='America/New_York'>Eastern Time</option>
                  <option value='America/Chicago'>Central Time</option>
                  <option value='America/Denver'>Mountain Time</option>
                  <option value='America/Los_Angeles'>Pacific Time</option>
                </select>
              </div>
              <button type='button' className={styles.saveButton} onClick={handleSave}>
                Save Preferences
              </button>
            </form>
          </div>
        );

      case 'notifications':
        return (
          <div className={styles.settingsSectionContent}>
            <h3>Notification Preferences</h3>
            <form className={styles.settingsForm}>
              <div className={`${styles.formGroup} ${styles.checkboxGroup}`}>
                <label>
                  <input
                    type='checkbox'
                    checked={settingsData.notifications.email}
                    onChange={(e) => handleInputChange('notifications', 'email', e.target.checked)}
                  />
                  Email Notifications
                </label>
                <small>Receive notifications via email</small>
              </div>
              <div className={`${styles.formGroup} ${styles.checkboxGroup}`}>
                <label>
                  <input
                    type='checkbox'
                    checked={settingsData.notifications.push}
                    onChange={(e) => handleInputChange('notifications', 'push', e.target.checked)}
                  />
                  Push Notifications
                </label>
                <small>Receive push notifications in your browser</small>
              </div>
              <div className={`${styles.formGroup} ${styles.checkboxGroup}`}>
                <label>
                  <input
                    type='checkbox'
                    checked={settingsData.notifications.marketing}
                    onChange={(e) => handleInputChange('notifications', 'marketing', e.target.checked)}
                  />
                  Marketing Emails
                </label>
                <small>Receive marketing and promotional emails</small>
              </div>
              <button type='button' className={styles.saveButton} onClick={handleSave}>
                Save Notification Settings
              </button>
            </form>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Layout title="Settings">
      <div className={styles.settingsContainer}>
        <div className={styles.settingsLayout}>
          {/* Settings Sidebar */}
          <aside className={styles.settingsSidebar}>
            <nav className={styles.settingsNav}>
              <ul className={styles.settingsNavList}>
                {settingsSections.map((section) => (
                  <li key={section.id} className={styles.settingsNavItem}>
                    <button
                      className={`${styles.settingsNavButton} ${activeSection === section.id ? styles.active : ''}`}
                      onClick={() => setActiveSection(section.id)}
                    >
                      <span className={styles.settingsNavIcon}>{section.icon}</span>
                      <span className={styles.settingsNavText}>
                        <span className={styles.settingsNavTitle}>{section.title}</span>
                        <span className={styles.settingsNavDescription}>{section.description}</span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>

          {/* Settings Content */}
          <main className={styles.settingsContent}>
            {renderSectionContent()}
          </main>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;