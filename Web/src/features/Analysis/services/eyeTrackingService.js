const API_BASE = '/api'

export async function fetchExperimentEyeTracking(experimentId) {
    const res = await fetch(`${API_BASE}/analysis/experiment/${experimentId}/eyetracking`)
    if (!res.ok) throw new Error(`Failed to fetch eye tracking: ${res.status}`)
    return res.json()
}
