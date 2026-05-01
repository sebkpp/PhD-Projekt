// src/features/Analysis/components/shared/LoadingSpinner.jsx
import React from 'react';

/**
 * Einfacher zentrierter Lade-Spinner.
 * Props:
 *   - message: string (optional)
 *   - size: number (optional, default 40)
 */
export default function LoadingSpinner({ message = 'Laden...', size = 40 }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px',
        gap: '12px',
        color: '#666',
      }}
    >
      <div
        style={{
          width: size,
          height: size,
          border: '4px solid #e0e0e0',
          borderTop: '4px solid #1976d2',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <span style={{ fontSize: '14px' }}>{message}</span>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
