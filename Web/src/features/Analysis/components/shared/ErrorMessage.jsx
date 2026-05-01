// src/features/Analysis/components/shared/ErrorMessage.jsx
import React from 'react';

/**
 * Fehler-Darstellung.
 * Props:
 *   - error: string | Error | null
 *   - onRetry: function (optional)
 */
export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '6px',
        backgroundColor: '#ffebee',
        border: '1px solid #f44336',
        color: '#c62828',
        fontSize: '13px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
      }}
    >
      <span>❌ {message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: '4px 12px',
            borderRadius: '4px',
            border: '1px solid #c62828',
            background: 'transparent',
            color: '#c62828',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Wiederholen
        </button>
      )}
    </div>
  );
}
