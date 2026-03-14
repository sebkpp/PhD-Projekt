// src/features/Analysis/components/CrossStudyChart.jsx
import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, ErrorBar } from 'recharts';
import DescriptiveOnlyWarning from './shared/DescriptiveOnlyWarning';

/**
 * Props:
 *   - data: { conditions: { name: {mean, ci_lower, ci_upper, n} }, baseline_ms: number, warning: string }
 *   - metric: string (z.B. "Transfer Duration (ms)")
 */
export default function CrossStudyChart({ data, metric = 'Transfer Duration' }) {
  if (!data || !data.conditions) {
    return <div style={{ color: '#999' }}>Keine Cross-Study-Daten verfügbar</div>;
  }

  const { conditions, baseline_ms, warning } = data;

  // Forest-Plot Daten: eine Zeile pro Bedingung
  const plotData = Object.entries(conditions).map(([name, stats], index) => ({
    y: index,
    x: stats.mean,
    name,
    ci_lower: stats.ci_lower,
    ci_upper: stats.ci_upper,
    n: stats.n,
    errorX: stats.mean !== null ? [(stats.mean - stats.ci_lower), (stats.ci_upper - stats.mean)] : [0, 0],
  })).filter(d => d.x !== null);

  const labels = plotData.map(d => d.name);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h3 style={{ margin: 0 }}>Cross-Study-Vergleich — {metric}</h3>
      <DescriptiveOnlyWarning message={warning} />

      <ResponsiveContainer width="100%" height={Math.max(200, plotData.length * 60 + 60)}>
        <ScatterChart margin={{ top: 10, right: 40, left: 60, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name="Mittelwert"
            label={{ value: metric, position: 'bottom', offset: -5 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={[-1, plotData.length]}
            tickFormatter={(v) => labels[v] || ''}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ payload }) => {
              if (!payload || payload.length === 0) return null;
              const d = payload[0]?.payload;
              if (!d) return null;
              return (
                <div style={{ background: '#fff', border: '1px solid #ccc', padding: '8px', borderRadius: '4px', fontSize: '12px' }}>
                  <div><strong>{d.name}</strong></div>
                  <div>Mittelwert: {d.x?.toFixed(1)}</div>
                  <div>95% CI: [{d.ci_lower?.toFixed(1)}, {d.ci_upper?.toFixed(1)}]</div>
                  <div>n = {d.n}</div>
                </div>
              );
            }}
          />
          {baseline_ms && (
            <ReferenceLine x={baseline_ms} stroke="#f57c00" strokeDasharray="6 3" label={{ value: `Baseline ${baseline_ms}ms`, fill: '#f57c00', fontSize: 11 }} />
          )}
          <Scatter data={plotData} fill="#1976d2">
            <ErrorBar dataKey="errorX" direction="x" stroke="#1976d2" strokeWidth={2} />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      {/* Tabelle darunter */}
      <table style={{ fontSize: '12px', borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr style={{ background: '#f5f5f5' }}>
            <th style={{ padding: '6px 12px', textAlign: 'left', border: '1px solid #e0e0e0' }}>Bedingung</th>
            <th style={{ padding: '6px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>Mittelwert</th>
            <th style={{ padding: '6px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>95% CI</th>
            <th style={{ padding: '6px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>n</th>
          </tr>
        </thead>
        <tbody>
          {plotData.map(({ name, x, ci_lower, ci_upper, n }) => (
            <tr key={name}>
              <td style={{ padding: '4px 12px', border: '1px solid #e0e0e0' }}>{name}</td>
              <td style={{ padding: '4px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>{x?.toFixed(2)}</td>
              <td style={{ padding: '4px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>[{ci_lower?.toFixed(2)}, {ci_upper?.toFixed(2)}]</td>
              <td style={{ padding: '4px 12px', textAlign: 'right', border: '1px solid #e0e0e0' }}>{n}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
