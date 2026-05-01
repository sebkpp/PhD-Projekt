// src/features/Analysis/components/shared/StatCard.jsx
import React from 'react';

/**
 * Zeigt eine einzelne Statistik-Kennzahl an.
 * Props:
 *   - label: string (z.B. "Transfer Duration")
 *   - value: string | number
 *   - unit: string (z.B. "ms", "%")
 *   - subtext: string (optional, z.B. "95% CI: [280, 320]")
 *   - highlight: boolean (optionales Hervorheben)
 */
export default function StatCard({ label, value, unit = '', subtext, highlight = false }) {
  return (
    <div
      style={{
        padding: '16px',
        borderRadius: '8px',
        border: highlight ? '2px solid #1976d2' : '1px solid #e0e0e0',
        backgroundColor: highlight ? '#e3f2fd' : '#fafafa',
        minWidth: '140px',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>{label}</div>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1a1a1a' }}>
        {value !== null && value !== undefined ? value : '—'}
        {unit && <span style={{ fontSize: '14px', color: '#666', marginLeft: '4px' }}>{unit}</span>}
      </div>
      {subtext && <div style={{ fontSize: '11px', color: '#888', marginTop: '4px' }}>{subtext}</div>}
    </div>
  );
}
