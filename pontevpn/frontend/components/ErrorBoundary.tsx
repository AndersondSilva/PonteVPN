"use client";
import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-brand-dark px-4 text-center">
          <div className="card max-w-md">
            <div className="text-5xl mb-4">🚧</div>
            <h1 className="text-2xl font-bold mb-2">Ops! Algo correu mal.</h1>
            <p className="text-white/50 mb-6">
              Ocorreu um erro inesperado na aplicação. Por favor, tente recarregar a página ou contacte o suporte se o problema persistir.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Recarregar Página
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
