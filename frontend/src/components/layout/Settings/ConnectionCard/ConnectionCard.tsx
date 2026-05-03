/**
 * ConnectionCard Component
 *
 * Reusable component for displaying third-party service connections.
 * Shows connection status, account info, and provides connect/disconnect actions.
 */

import React, { useState } from 'react';
import styles from './ConnectionCard.module.css';
import authService from '../../../../services/authService';
import { API_BASE_URL, API_ENDPOINTS } from '../../../../constants';

interface ConnectionCardProps {
  service: string;
  isConnected: boolean;
  connectedAt?: string;
  syncActivities: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onSyncToggle: (enabled: boolean) => void;
}

/**
 * Connected Card component for managing third party integrations
 */
const ConnectionCard: React.FC<ConnectionCardProps> = ({
  service,
  isConnected,
  // connectedAt,
  // syncActivities,
  // onConnect,
  onDisconnect,
  // onSyncToggle
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleConnect = async () => {
    setIsLoading(true);

    const token = authService.getToken();
    if (!token) {
      console.error('No token found');
      alert('Please login first');
      setIsLoading(false);
      return;
    }

    try{
      const response = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.STRAVA.CONNECT}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to connect to Strava');
      }

      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Error connecting to Strava:', error);
      alert('Failed to connect to Strava. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.connectionCard}>
      <h3>{service} Connection</h3>
      <p>Status: {isConnected ? 'Connected' : 'Not Connected'}</p>

      <button
        className={styles.actionButton}
        onClick={isConnected ? onDisconnect : handleConnect}
        disabled={isLoading}
      >
        {isConnected ? 'Disconnect' : isLoading ? 'Connecting...' : 'Connect'}
      </button>
    </div>
  );
};

export default ConnectionCard;
