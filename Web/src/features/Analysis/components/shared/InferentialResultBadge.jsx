// src/features/Analysis/components/shared/InferentialResultBadge.jsx
import React from 'react';

/**
 * Zeigt das Ergebnis eines inferentiellen Tests als Badge an.
 * Props:
 *   - result: object aus InferentialResult (test_used, main_effect, posthoc)
 */

const TEST_LABELS = {
  rm_anova: 'RM-ANOVA',
  rm_anova_gg: 'RM-ANOVA (GG-korr.)',
  friedman: 'Friedman',
  paired_t: 'Paired t-Test',
  wilcoxon: 'Wilcoxon',
};

function SignificanceBadge({ significant, pValue }) {
  const color = significant ? '#2e7d32' : '#757575';
  const bg = significant ? '#e8f5e9' : '#f5f5f5';
  const label = significant ? 'Signifikant' : 'Nicht signifikant';
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '12px',
        backgroundColor: bg,
        color,
        fontSize: '12px',
        fontWeight: 'bold',
        border: `1px solid ${color}`,
      }}
    >
      {label}{pValue !== null && pValue !== undefined ? ` (p=${pValue})` : ''}
    </span>
  );
}

export default function InferentialResultBadge({ result }) {
  if (!result) return <span style={{ color: '#999', fontSize: '13px' }}>Keine Analyse</span>;

  const { test_used, main_effect, posthoc } = result;
  const testLabel = TEST_LABELS[test_used] || test_used;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ fontSize: '13px', color: '#555' }}>
        Test: <strong>{testLabel}</strong>
      </div>

      {main_effect && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '13px' }}>Haupteffekt:</span>
          <SignificanceBadge
            significant={main_effect.significant}
            pValue={main_effect.p_value}
          />
          {main_effect.effect_size !== null && main_effect.effect_size !== undefined && (
            <span style={{ fontSize: '12px', color: '#555' }}>
              {main_effect.effect_size_type || 'η²p'} = {main_effect.effect_size}
            </span>
          )}
        </div>
      )}

      {posthoc && posthoc.length > 0 && (
        <div>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
            Post-hoc ({posthoc.length} Paare):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {posthoc.map((pair, i) => (
              <span
                key={i}
                style={{
                  fontSize: '11px',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: pair.significant ? '#e8f5e9' : '#f5f5f5',
                  color: pair.significant ? '#2e7d32' : '#757575',
                  border: `1px solid ${pair.significant ? '#2e7d32' : '#ccc'}`,
                }}
              >
                {pair.condition_a} vs {pair.condition_b}
                {pair.p_corrected !== null && pair.p_corrected !== undefined
                  ? ` p=${pair.p_corrected}`
                  : ''}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
