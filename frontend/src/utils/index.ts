/**
 * Utility functions for common operations
 */

// Storage utilities
export const storage = {
  get: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.warn(`Failed to get item from localStorage: ${key}`, error);
      return null;
    }
  },

  set: (key: string, value: string): void => {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.warn(`Failed to set item in localStorage: ${key}`, error);
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Failed to remove item from localStorage: ${key}`, error);
    }
  },

  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.warn('Failed to clear localStorage', error);
    }
  },
};

