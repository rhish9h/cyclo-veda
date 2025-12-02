/**
 * ConnectionCard Component
 *
 * Reusable component for displaying third-party service connections.
 * Shows connection status, account info, and provides connect/disconnect actions.
 */

import React from 'react';
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
    // onConnect,
    onDisconnect,
    // onSyncToggle
}) => {
    const handleConnect = () => {
        // Use form submission for OAuth to handle redirects (and cookies in the future) correctly
        window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/strava/connect`;
    }

    return (
        <div className={styles.connectionCard}>
            <h3>{service} Connection</h3>
            <p>
                Status: {isConnected ? 'Connected' : 'Not Connected'}
            </p>

            <button 
                className={styles.actionButton}
                onClick={isConnected ? onDisconnect : handleConnect}
            >
                {isConnected ? 'Disconnect' : 'Connect'}
            </button>
        </div>
    );
};

export default ConnectionCard;