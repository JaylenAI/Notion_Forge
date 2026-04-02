import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error.message, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center bg-[var(--bg,#131313)]">
          <div className="text-center p-8 max-w-md">
            <span className="material-symbols-outlined text-4xl text-[#ffb4ab] mb-4 block">error</span>
            <h2 className="text-lg font-bold text-[var(--text-primary,#e5e2e1)] mb-2">오류가 발생했습니다</h2>
            <p className="text-sm text-[var(--text-muted,#c2c6d8)] mb-4">
              {this.state.error?.message?.slice(0, 100) ?? "알 수 없는 오류"}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                type="button"
                onClick={this.handleReset}
                className="px-4 py-2 rounded-lg bg-[#adc6ff] text-[#002e69] text-sm font-medium hover:opacity-90"
              >
                다시 시도
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 rounded-lg bg-[var(--surface-variant,#353534)] text-[var(--text-muted,#c2c6d8)] text-sm font-medium hover:opacity-90"
              >
                새로고침
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
