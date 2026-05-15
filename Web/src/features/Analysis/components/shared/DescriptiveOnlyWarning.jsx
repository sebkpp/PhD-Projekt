// src/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx
import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Zeigt einen Warnhinweis für deskriptive Cross-Study-Vergleiche.
 * Props:
 *   - message: string (optional, überschreibt Standard-Text)
 */
export default function DescriptiveOnlyWarning({ message }) {
  const { t } = useTranslation('analysis');
  const text = message || t('shared.descriptiveOnlyDefault');
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '6px',
        backgroundColor: '#fff8e1',
        border: '1px solid #ffc107',
        color: '#7b5800',
        fontSize: '13px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '8px',
      }}
    >
      <span style={{ fontSize: '16px', flexShrink: 0 }}>⚠️</span>
      <span>{text}</span>
    </div>
  );
}
