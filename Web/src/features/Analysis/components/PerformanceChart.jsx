// src/features/Analysis/components/PerformanceChart.jsx
import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ErrorBar,
  ResponsiveContainer,
} from 'recharts';
import { getStudyPerformance } from '../services/inferentialAnalysisService';
import InferentialResultBadge from './shared/InferentialResultBadge';
import LoadingSpinner from './shared/LoadingSpinner';
import ErrorMessage from './shared/ErrorMessage';
import StatCard from './shared/StatCard';

/**
 * Zeigt Performance-Metriken (Transferzeiten) pro Bedingung als Balkendiagramm
 * mit Fehlerbalken (Std-Abweichung), aufgeteilt nach Phasen.
 *
 * Props:
 *   - studyId: number
 */

const PHASES = [
  { key: 'total', label: 'Gesamt', meanKey: 'total_mean', stdKey: 'total_std', nKey: 'n' },
  { key: 'phase1', label: 'Phase 1 (Coordination)', meanKey: 'phase1_mean', stdKey: 'phase1_std', nKey: 'n' },
  { key: 'phase2', label: 'Phase 2 (Grasp)', meanKey: 'phase2_mean', stdKey: 'phase2_std', nKey: 'n' },
  { key: 'phase3', label: 'Phase 3 (Transfer)', meanKey: 'phase3_mean', stdKey: 'phase3_std', nKey: 'n' },
];

const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c62828'];

function buildChartData(byCondition, phase) {
  return Object.entries(byCondition || {}).map(([condition, stats], i) => ({
    condition,
    mean: stats[phase.meanKey] ?? 0,
    error: stats[phase.stdKey] ?? 0,
    n: stats[phase.nKey] ?? 0,
    fill: COLORS[i % COLORS.length],
  }));
}

export default function PerformanceChart({ studyId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPhaseKey, setSelectedPhaseKey] = useState('total');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getStudyPerformance(studyId);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [studyId]);

  if (loading) return <LoadingSpinner message="Performance-Daten laden..." />;
  if (error) return <ErrorMessage error={error} onRetry={fetchData} />;
  if (!data?.performance?.by_condition) {
    return <div style={{ color: '#999' }}>Keine Performance-Daten verfügbar</div>;
  }

  const { by_condition, inferential } = data.performance;
  const selectedPhase = PHASES.find(p => p.key === selectedPhaseKey) || PHASES[0];
  const chartData = buildChartData(by_condition, selectedPhase);
  const inferentialResult = inferential?.[selectedPhaseKey];

  const yLabel = selectedPhaseKey === 'total' || selectedPhaseKey.startsWith('phase')
    ? 's'
    : 's';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h3 style={{ margin: 0 }}>Performance-Analyse — Studie {studyId}</h3>

      {/* Phasen-Auswahl */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {PHASES.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSelectedPhaseKey(key)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              border: 'none',
              background: selectedPhaseKey === key ? '#1976d2' : '#e0e0e0',
              color: selectedPhaseKey === key ? '#fff' : '#333',
              cursor: 'pointer',
              fontSize: '13px',
              transition: 'background 0.15s',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {chartData.map(({ condition, mean, n }) => (
          <StatCard
            key={condition}
            label={condition}
            value={mean !== undefined && mean !== null ? mean.toFixed(2) : '—'}
            unit="s"
            subtext={`n=${n}`}
          />
        ))}
      </div>

      {/* Balkendiagramm mit Fehlerbalken */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="condition" />
          <YAxis
            label={{ value: yLabel, angle: -90, position: 'insideLeft', offset: 5 }}
          />
          <Tooltip
            formatter={(value, name) => [
              name === 'mean'
                ? `${value !== null ? value.toFixed(2) : '—'} s`
                : `±${value !== null ? value.toFixed(2) : '—'} s`,
              name === 'mean' ? 'Mittelwert' : 'Std-Abweichung',
            ]}
          />
          <Bar dataKey="mean" fill="#1976d2" name="Mittelwert">
            <ErrorBar dataKey="error" width={4} strokeWidth={2} stroke="#f57c00" />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Inferentielle Analyse */}
      {inferentialResult && (
        <div
          style={{
            padding: '12px',
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            backgroundColor: '#fafafa',
          }}
        >
          <div style={{ fontSize: '13px', color: '#555', marginBottom: '8px' }}>
            Inferentielle Analyse ({selectedPhase.label}):
          </div>
          <InferentialResultBadge result={inferentialResult} />
        </div>
      )}

      {/* Bedingungsanzahl-Info */}
      <div style={{ fontSize: '12px', color: '#888' }}>
        {data.n_experiments} Experimente · {Object.keys(by_condition).length} Bedingungen
      </div>
    </div>
  );
}
