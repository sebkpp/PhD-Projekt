const API_BASE = '/api'

export async function fetchExperimentEyeTracking(experimentId) {
    const res = await fetch(`${API_BASE}/analysis/experiment/${experimentId}/eyetracking`)
    if (!res.ok) throw new Error(`Failed to fetch eye tracking: ${res.status}`)
    return res.json()
}

export async function fetchExperimentEyeTrackingPhases(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/phases`);
    if (!res.ok) throw new Error(`Failed to fetch ET phases: ${res.status}`);
    return res.json();
}

export async function fetchExperimentEyeTrackingTransitions(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/transitions`);
    if (!res.ok) throw new Error(`Failed to fetch ET transitions: ${res.status}`);
    return res.json();
}

export async function fetchExperimentPPI(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/ppi`);
    if (!res.ok) throw new Error(`Failed to fetch PPI: ${res.status}`);
    return res.json();
}

export async function fetchExperimentSaccadeRate(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/saccade-rate`);
    if (!res.ok) throw new Error(`Saccade rate fetch failed: ${res.status}`);
    return res.json();
}
