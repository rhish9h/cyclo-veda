/**
 * Strava Service
 *
 * Handles all Strava API interactions for the frontend.
 */

import { API_BASE_URL, API_ENDPOINTS } from "../constants";
import authService from "./authService";

interface StravaStatus {
    connected: boolean;
    athlete_id?: number;
    expires_at?: string;
    is_expiring_soon?: boolean;
    has_refresh_token?: boolean;
    scope?: string;
}

const stravaService = {
    /**
     * Fetch the current Strava connection status for the authenticated user
     */
    async getStatus(): Promise<StravaStatus | null> {
        const token = authService.getToken();
        if (!token) {
            return null;
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}${API_ENDPOINTS.STRAVA.STATUS}`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to fetch Strava status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching Strava status:', error);
            return null;
        }
    },
    /**
     * Disconnect the current Strava connection for the authenticated user
     */
    async disconnect(): Promise<boolean> {
        const token = authService.getToken();
        if (!token) {
            return false;
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}${API_ENDPOINTS.STRAVA.DISCONNECT}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                }
            );

            if (response.ok) {
                return true;
            }

            throw new Error(`Failed to disconnect: ${response.status}`);
        } catch (error) {
            console.error('Error disconnecting Strava:', error);
            return false;
        }
    },
};

export default stravaService;