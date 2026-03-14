// src/features/Analysis/components/EyeTrackingChart.jsx
import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getStudyEyeTracking } from '../services/inferentialAnalysisService';
import LoadingSpinner from './shared/LoadingSpinner';
import ErrorMessage from './shared/ErrorMessage';
import StatCard from './shared/StatCard';

/**
 * Zeigt Eye-Tracking-Daten als gestapeltes Balkendiagramm (Stacked Bar).
 * AOI Dwell-Time als Prozentsatz der Gesamtblickzeit, pro Bedingung.
 *
 * Daten-Format aus getStudyEyeTracking():
 *   {
 *     study_id, n_experiments, conditions,
 *     by_condition: {
 *       [conditionName]: {
 *         total_duration_ms: number,
 *         aoi_stats: {
 *           [aoiKey]: {
 *             label: string,
 *             total_duration_ms: number,
 *             percentage: number,      // 0–100 Prozent der Gesamtblickzeit
 *             fixation_count: number,
 *             mean_duration_ms: number,
 *           }
 *         }
 *       }
 *     }
 *   }
 *
 * Props:
 *   - studyId: number
 */

const AOI_COLORS = {
  object: '#1976d2',
  hand: '#388e3c',
  partner_hand: '#f57c00',
  environment: '#7b1fa2',
  face: '#c62828',
  screen: '#0097a7',
};

const FALLBACK_COLORS = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c62828', '#0097a7', '#795548', '#607d8b'];

function getAoiColor(aoiKey, index) {
  return AOI_COLORS[aoiKey] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

/** Tooltip-Formatter: zeigt Prozentwert und Fixationsanzahl. */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #e0e0e0',
        borderRadius: '6px',
        padding: '10px 14px',
        fontSize: '13px',
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>{label}</div>
      {payload.map((entry) => (
        <div key={entry.dataKey} style={{ color: entry.fill, marginBottom: '2px' }}>
          {entry.name}: {entry.value !== null ? entry.value.toFixed(1) : '—'}%
        </div>
      ))}
    </div>
  );
}

export default function EyeTrackingChart({ studyId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getStudyEyeTracking(studyId);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [studyId]);

  if (loading) return <LoadingSpinner message="Eye-Tracking-Daten laden..." />;
  if (error) return <ErrorMessage error={error} onRetry={fetchData} />;
  if (!data || !data.by_condition || Object.keys(data.by_condition).length === 0) {
    return <div style={{ color: '#999' }}>Keine Eye-Tracking-Daten verfügbar</div>;
  }

  const conditions = Object.keys(data.by_condition);

  // Alle AOI-Schlüssel (union) über alle Bedingungen sammeln
  const allAoiKeys = [
    ...new Set(
      conditions.flatMap(c => Object.keys(data.by_condition[c]?.aoi_stats || {}))
    ),
  ];

  // AOI-Label-Map aufbauen (erste Bedingung die den AOI kennt, liefert das Label)
  const aoiLabelMap = {};
  allAoiKeys.forEach(aoiKey => {
    for (const c of conditions) {
      const stat = data.by_condition[c]?.aoi_stats?.[aoiKey];
      if (stat?.label) {
        aoiLabelMap[aoiKey] = stat.label;
        break;
      }
    }
    if (!aoiLabelMap[aoiKey]) aoiLabelMap[aoiKey] = aoiKey;
  });

  // Chart-Daten: eine Zeile pro Bedingung, Spalten = AOI-Schlüssel (Prozentwert)
  const chartData = conditions.map(condition => {
    const condStats = data.by_condition[condition]?.aoi_stats || {};
    const row = { condition };
    allAoiKeys.forEach(aoiKey => {
      row[aoiKey] = condStats[aoiKey]?.percentage ?? 0;
    });
    return row;
  });

  // Gesamtblickzeit-Stat-Cards pro Bedingung
  const totalMsData = conditions.map(c => ({
    condition: c,
    total_ms: data.by_condition[c]?.total_duration_ms,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h3 style={{ margin: 0 }}>Eye-Tracking — Studie {studyId}</h3>

      {/* Gesamtblickzeit-Karten */}
      {totalMsData.some(d => d.total_ms !== undefined) && (
        <div>
          <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
            Gesamtblickzeit pro Bedingung:
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {totalMsData.map(({ condition, total_ms }) => (
              <StatCard
                key={condition}
                label={condition}
                value={total_ms !== undefined && total_ms !== null
                  ? (total_ms / 1000).toFixed(1)
                  : '—'}
                unit="s"
                subtext="Gesamtblickzeit"
              />
            ))}
          </div>
        </div>
      )}

      {/* Stacked Bar: AOI Dwell-Time in Prozent */}
      {chartData.length > 0 && allAoiKeys.length > 0 ? (
        <>
          <div style={{ fontSize: '13px', color: '#555' }}>
            AOI Dwell-Time (% der Gesamtblickzeit):
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="condition" />
              <YAxis
                domain={[0, 100]}
                tickFormatter={v => `${v}%`}
                label={{ value: '%', angle: -90, position: 'insideLeft', offset: 5 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => aoiLabelMap[value] || value}
              />
              {allAoiKeys.map((aoiKey, i) => (
                <Bar
                  key={aoiKey}
                  dataKey={aoiKey}
                  stackId="aoi"
                  fill={getAoiColor(aoiKey, i)}
                  name={aoiLabelMap[aoiKey] || aoiKey}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </>
      ) : (
        <div style={{ color: '#999' }}>Keine AOI-Daten vorhanden</div>
      )}

      {/* Fixationsanzahl-Tabelle */}
      {allAoiKeys.length > 0 && (
        <div>
          <div style={{ fontSize: '13px', color: '#555', marginBottom: '8px' }}>
            Fixationsanzahl pro AOI und Bedingung:
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{
                borderCollapse: 'collapse',
                fontSize: '12px',
                width: '100%',
                maxWidth: '600px',
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      textAlign: 'left',
                      padding: '6px 10px',
                      borderBottom: '1px solid #e0e0e0',
                      color: '#555',
                      fontWeight: 600,
                    }}
                  >
                    AOI
                  </th>
                  {conditions.map(c => (
                    <th
                      key={c}
                      style={{
                        textAlign: 'right',
                        padding: '6px 10px',
                        borderBottom: '1px solid #e0e0e0',
                        color: '#555',
                        fontWeight: 600,
                      }}
                    >
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {allAoiKeys.map((aoiKey, i) => (
                  <tr key={aoiKey} style={{ background: i % 2 === 0 ? '#fafafa' : '#fff' }}>
                    <td style={{ padding: '5px 10px', color: '#333' }}>
                      <span
                        style={{
                          display: 'inline-block',
                          width: '10px',
                          height: '10px',
                          borderRadius: '2px',
                          backgroundColor: getAoiColor(aoiKey, i),
                          marginRight: '6px',
                          verticalAlign: 'middle',
                        }}
                      />
                      {aoiLabelMap[aoiKey] || aoiKey}
                    </td>
                    {conditions.map(c => {
                      const count = data.by_condition[c]?.aoi_stats?.[aoiKey]?.fixation_count;
                      return (
                        <td
                          key={c}
                          style={{
                            textAlign: 'right',
                            padding: '5px 10px',
                            color: '#444',
                          }}
                        >
                          {count !== undefined && count !== null ? count : '—'}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Meta-Informationen */}
      <div style={{ fontSize: '12px', color: '#888' }}>
        {data.n_experiments} Experimente · {conditions.length} Bedingungen · {allAoiKeys.length} AOIs
      </div>
    </div>
  );
}
