/**
 * Entry point for the Cyclo Veda React application
 * Sets up the root component with error boundaries and proper error handling
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { DOM_ELEMENTS } from './constants';
import { logError } from './utils/errorHandler';
import { ErrorBoundary } from './components/ErrorBoundary';
import App from './App';
import './index.css';

/**
 * Initialize and render the React application
 * Includes error boundary and proper root element validation
 */
function initializeApp(): void {
  // Get the root DOM element
  const rootElement = document.getElementById(DOM_ELEMENTS.ROOT_ID);

  if (!rootElement) {
    const error = new Error(
      `Failed to find root element with ID '${DOM_ELEMENTS.ROOT_ID}'. ` +
        'Please ensure the HTML contains a div with this ID.'
    );
    logError(error, 'App Initialization');
    throw error;
  }

  // Create the React root
  const root = createRoot(rootElement);

  // Render the application with error boundary
  root.render(
    <ErrorBoundary>
      {import.meta.env.DEV ? (
        <StrictMode>
          <App />
        </StrictMode>
      ) : (
        <App />
      )}
    </ErrorBoundary>
  );
}

// Initialize the application with error handling
try {
  initializeApp();
} catch (error) {
  // Fallback error display if even the error boundary fails
  const rootElement = document.getElementById(DOM_ELEMENTS.ROOT_ID);
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        font-family: system-ui, -apple-system, sans-serif;
        background-color: #f9fafb;
      ">
        <div style="
          max-width: 400px;
          padding: 2rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          text-align: center;
        ">
          <h1 style="color: #dc2626; margin-bottom: 1rem;">Application Error</h1>
          <p style="color: #6b7280; margin-bottom: 1rem;">
            Failed to initialize the application. Please refresh the page or contact support.
          </p>
          <button 
            onclick="window.location.reload()" 
            style="
              background: #3b82f6;
              color: white;
              border: none;
              padding: 0.5rem 1rem;
              border-radius: 4px;
              cursor: pointer;
            "
          >
            Refresh Page
          </button>
        </div>
      </div>
    `;
  } else {
    // Last resort: show alert if we can't even find the root element
    alert(
      'Critical error: Unable to initialize the application. Please refresh the page.'
    );
  }
}
