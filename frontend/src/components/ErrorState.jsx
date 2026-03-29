// frontend/src/components/ErrorState.jsx
export default function ErrorState({ message, onRetry }) {
  return (
    <div className="chart-card">
      <div className="error-box">
        <div className="error-icon">⚠️</div>
        <div className="error-title">Failed to load data</div>
        <div className="error-msg">
          {message || 'Could not connect to the API. Make sure the backend is running on port 8000.'}
        </div>
        {onRetry && (
          <button className="btn-retry" onClick={onRetry}>
            ↺ Retry
          </button>
        )}
      </div>
    </div>
  )
}
