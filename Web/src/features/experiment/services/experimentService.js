const API_BASE = "/api";

export async function createExperiment({ experimentSettings }) {
    const res = await fetch(`${API_BASE}/experiments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ experimentSettings })
    })

    if (!res.ok) {
        throw new Error('Fehler beim Anlegen des Experiments.')
    }

    return res.json()
}

export async function getExperimentsByStudy(study_id) {
    const response = await fetch(`${API_BASE}/studies/${study_id}/experiments`);
    if (!response.ok) throw new Error("Fehler beim Laden der Experimente");
    return await response.json();
}