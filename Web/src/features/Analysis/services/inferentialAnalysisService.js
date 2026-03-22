const API_BASE = '/api/analysis';

async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

export const getStudyPerformance = async (studyId) => {
    const response = await fetch(`${API_BASE}/study/${studyId}/performance`);
    return handleResponse(response);
};

export const getStudyEyeTracking = async (studyId) => {
    const response = await fetch(`${API_BASE}/study/${studyId}/eye-tracking`);
    return handleResponse(response);
};

export const postCorrelation = async (variables) => {
    const response = await fetch(`${API_BASE}/correlation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ variables }),
    });
    return handleResponse(response);
};

export const postCrossStudy = async (studyData, metric = 'transfer_duration_ms') => {
    const response = await fetch(`${API_BASE}/cross-study`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ study_data: studyData, metric }),
    });
    return handleResponse(response);
};

export const postPCA = async (data, nComponents = 2) => {
    const response = await fetch(`${API_BASE}/pca`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data, n_components: nComponents }),
    });
    return handleResponse(response);
};

export const postClustering = async (data, nClusters = 3) => {
    const response = await fetch(`${API_BASE}/clustering`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data, n_clusters: nClusters }),
    });
    return handleResponse(response);
};

export const downloadStudyCsv = async (studyId) => {
    const response = await fetch(`${API_BASE}/study/${studyId}/export/csv`);
    if (!response.ok) {
        throw new Error(`Export failed: HTTP ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `handovers_study_${studyId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
};

export const downloadStudyXlsx = async (studyId) => {
    const response = await fetch(`${API_BASE}/study/${studyId}/export/xlsx`);
    if (!response.ok) {
        throw new Error(`Export failed: HTTP ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `handovers_study_${studyId}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
};
