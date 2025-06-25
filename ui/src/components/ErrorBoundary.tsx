import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    console.error('Error stack:', error.stack);
    console.error('Component stack:', errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div 
          className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900"
          data-testid="error-boundary"
        >
          <div className="max-w-md w-full mx-auto text-center p-6">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
                Something went wrong
              </h2>
              <p className="text-red-600 dark:text-red-300 mb-4">
                An unexpected error occurred. Please refresh the page to try again.
              </p>
              {this.state.error && process.env.NODE_ENV === 'development' && (
                <details className="text-left">
                  <summary className="cursor-pointer text-sm text-red-700 dark:text-red-300 mb-2">
                    Error Details (Development)
                  </summary>
                  <pre className="text-xs text-red-800 dark:text-red-200 bg-red-100 dark:bg-red-900/30 p-2 rounded overflow-auto">
                    {this.state.error.toString()}
                    {'\n\n'}
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;