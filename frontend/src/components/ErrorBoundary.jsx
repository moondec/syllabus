import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '8px', margin: '20px' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Coś poszło nie tak (Błąd aplikacji)</h2>
          <details style={{ whiteSpace: 'pre-wrap', marginTop: '10px' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>Pokaż szczegóły błędu</summary>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
          <button 
             onClick={() => window.location.reload()} 
             style={{ marginTop: '10px', padding: '8px 16px', background: '#dc2626', color: 'white', borderRadius: '4px' }}>
             Odśwież stronę
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
