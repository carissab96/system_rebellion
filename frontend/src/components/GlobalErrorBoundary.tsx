import React from "react";

type State = { hasError: boolean; info?: string; error?: string };

export class GlobalErrorBoundary extends React.Component<React.PropsWithChildren, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(err: unknown): State {
    return { hasError: true, error: err instanceof Error ? err.message : String(err) };
  }

  componentDidCatch(error: unknown, info: any) {
    // eslint-disable-next-line no-console
    console.error("GlobalErrorBoundary caught:", error, info);
    this.setState({ info: info?.componentStack || "" });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16, fontFamily: "ui-sans-serif, system-ui" }}>
          <h1>💥 Something exploded</h1>
          <pre style={{ whiteSpace: "pre-wrap" }}>{this.state.error}</pre>
          {this.state.info && (
            <>
              <h3>Where</h3>
              <pre style={{ whiteSpace: "pre-wrap" }}>{this.state.info}</pre>
            </>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}
