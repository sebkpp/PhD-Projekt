// src/features/Analysis/pages/AnalysisDashboard.jsx
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import PerformanceChart from '../components/PerformanceChart';
import EyeTrackingChart from '../components/EyeTrackingChart';
import { downloadStudyCsv, downloadStudyXlsx } from '../services/inferentialAnalysisService';

const TABS = [
  { key: 'performance', label: 'Performance' },
  { key: 'eyetracking', label: 'Eye-Tracking' },
  { key: 'export', label: 'Export' },
];

export default function AnalysisDashboard() {
  const { studyId } = useParams();
  const [activeTab, setActiveTab] = useState('performance');
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async (format) => {
    setDownloading(true);
    try {
      if (format === 'csv') await downloadStudyCsv(studyId);
      else await downloadStudyXlsx(studyId);
    } catch (err) {
      alert(`Download fehlgeschlagen: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ margin: '0 0 20px' }}>Analyse — Studie {studyId}</h2>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', borderBottom: '2px solid #e0e0e0', marginBottom: '24px' }}>
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderBottom: activeTab === key ? '3px solid #1976d2' : '3px solid transparent',
              background: 'transparent',
              color: activeTab === key ? '#1976d2' : '#555',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === key ? 'bold' : 'normal',
              marginBottom: '-2px',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab-Inhalte */}
      {activeTab === 'performance' && <PerformanceChart studyId={studyId} />}
      {activeTab === 'eyetracking' && <EyeTrackingChart studyId={studyId} />}
      {activeTab === 'export' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '400px' }}>
          <h3 style={{ margin: 0 }}>Daten exportieren</h3>
          <p style={{ color: '#666', fontSize: '14px' }}>
            Alle Handover-Daten der Studie als Datei herunterladen.
          </p>
          <button
            onClick={() => handleDownload('csv')}
            disabled={downloading}
            style={{
              padding: '12px 20px',
              borderRadius: '6px',
              border: '1px solid #1976d2',
              background: '#1976d2',
              color: '#fff',
              cursor: downloading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            {downloading ? 'Lädt...' : 'CSV herunterladen'}
          </button>
          <button
            onClick={() => handleDownload('xlsx')}
            disabled={downloading}
            style={{
              padding: '12px 20px',
              borderRadius: '6px',
              border: '1px solid #388e3c',
              background: '#388e3c',
              color: '#fff',
              cursor: downloading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            {downloading ? 'Lädt...' : 'Excel (XLSX) herunterladen'}
          </button>
        </div>
      )}
    </div>
  );
}
