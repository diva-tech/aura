"use client";

import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error boundary caught:", error, errorInfo);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-slate-900 to-slate-950 px-4">
          <div className="max-w-md text-center">
            <AlertTriangle size={48} className="mx-auto mb-4 text-red-400" />
            <h1 className="text-2xl font-bold text-white mb-2">
              Something went wrong
            </h1>
            <p className="text-slate-400 mb-6">
              We're sorry, but something unexpected happened. Please try again
              or contact support if the problem persists.
            </p>

            {process.env.NODE_ENV === "development" && (
              <details className="mb-6 text-left bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <summary className="cursor-pointer text-sm font-medium text-slate-300 hover:text-white transition-colors">
                  Error details
                </summary>
                <pre className="mt-2 text-xs text-slate-400 overflow-auto max-h-32">
                  {this.state.error?.toString()}
                </pre>
              </details>
            )}

            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
            >
              <RefreshCw size={18} />
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
