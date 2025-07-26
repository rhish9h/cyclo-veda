/**
 * Centralized error handling utilities
 */

import { ERROR_MESSAGES } from '../constants';

export interface AppError {
  message: string;
  code?: string;
  status?: number;
  details?: unknown;
}

export class ApiError extends Error implements AppError {
  public code?: string;
  public status?: number;
  public details?: unknown;

  constructor(
    message: string,
    status?: number,
    code?: string,
    details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class ValidationError extends Error implements AppError {
  public code?: string;
  public details?: unknown;

  constructor(message: string, code?: string, details?: unknown) {
    super(message);
    this.name = 'ValidationError';
    this.code = code;
    this.details = details;
  }
}

export const errorHandler = {
  /**
   * Handle API errors and convert them to user-friendly messages
   */
  handleApiError: (error: unknown): AppError => {
    if (error instanceof ApiError) {
      return error;
    }

    if (error instanceof Error) {
      // Network errors
      if (error.message.includes('fetch')) {
        return {
          message: ERROR_MESSAGES.NETWORK,
          code: 'NETWORK_ERROR',
        };
      }

      return {
        message: error.message || ERROR_MESSAGES.GENERIC,
        code: 'UNKNOWN_ERROR',
      };
    }

    return {
      message: ERROR_MESSAGES.GENERIC,
      code: 'UNKNOWN_ERROR',
      details: error,
    };
  },

  /**
   * Handle validation errors
   */
  handleValidationError: (
    field: string,
    value: unknown
  ): ValidationError | null => {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return new ValidationError(`${field} is required`, 'REQUIRED_FIELD');
    }
    return null;
  },

  /**
   * Log errors for debugging (in development) or monitoring (in production)
   */
  logError: (error: AppError | Error, context?: string): void => {
    const errorInfo = {
      message: error.message,
      name: error instanceof Error ? error.name : 'AppError',
      stack: error instanceof Error ? error.stack : undefined,
      context,
      timestamp: new Date().toISOString(),
    };

    if (import.meta.env.DEV) {
      console.error('Error logged:', errorInfo);
    } else {
      // In production, you might want to send this to a monitoring service
      // Example: sendToMonitoringService(errorInfo);
    }
  },

  /**
   * Create a user-friendly error message from an error object
   */
  getDisplayMessage: (error: AppError | Error): string => {
    if ('status' in error) {
      switch (error.status) {
        case 400:
          return ERROR_MESSAGES.VALIDATION;
        case 401:
          return ERROR_MESSAGES.UNAUTHORIZED;
        case 403:
          return ERROR_MESSAGES.UNAUTHORIZED;
        case 404:
          return 'The requested resource was not found.';
        case 500:
          return 'Server error. Please try again later.';
        default:
          return error.message || ERROR_MESSAGES.GENERIC;
      }
    }

    return error.message || ERROR_MESSAGES.GENERIC;
  },
};

// Export individual functions for convenience
export const {
  handleApiError,
  handleValidationError,
  logError,
  getDisplayMessage,
} = errorHandler;
