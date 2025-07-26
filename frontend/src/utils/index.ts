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

// String utilities
export const formatString = {
  capitalize: (str: string): string =>
    str.charAt(0).toUpperCase() + str.slice(1).toLowerCase(),

  truncate: (str: string, maxLength: number): string =>
    str.length > maxLength ? `${str.slice(0, maxLength)}...` : str,

  slugify: (str: string): string =>
    str
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, ''),
};

// Validation utilities
export const validation = {
  isEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  isStrongPassword: (password: string): boolean => {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  },

  isEmpty: (value: unknown): boolean => {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string') return value.trim().length === 0;
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
  },
};

// Date utilities
export const dateUtils = {
  formatDate: (date: Date | string, locale = 'en-US'): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString(locale);
  },

  formatDateTime: (date: Date | string, locale = 'en-US'): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleString(locale);
  },

  isValidDate: (date: unknown): boolean => {
    return date instanceof Date && !isNaN(date.getTime());
  },
};

// Async utilities
export const asyncUtils = {
  delay: (ms: number): Promise<void> =>
    new Promise(resolve => setTimeout(resolve, ms)),

  retry: async <T>(
    fn: () => Promise<T>,
    maxAttempts = 3,
    delayMs = 1000
  ): Promise<T> => {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        if (attempt === maxAttempts) break;
        await asyncUtils.delay(delayMs * attempt);
      }
    }

    throw lastError!;
  },
};

// CSS class utilities
export const classNames = (
  ...classes: (string | undefined | null | false)[]
): string => {
  return classes.filter(Boolean).join(' ');
};
