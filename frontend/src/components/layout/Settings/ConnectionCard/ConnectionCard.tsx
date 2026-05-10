/**
 * ConnectionCard Component
 *
 * Reusable component for displaying third-party service connections.
 * Shows connection status, account info, and provides connect/disconnect actions.
 */

import React, { useState } from 'react';
import styles from './ConnectionCard.module.css';

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
  onConnect,
  onDisconnect,
  // onSyncToggle
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleConnect = async () => {
    setIsLoading(true);
    try {
      await onConnect();
    } catch (error) {
      console.error('Failed to connect to Strava');
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
