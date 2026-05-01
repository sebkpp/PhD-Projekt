const API_BASE = '/api'

export async function fetchStudyPerformance(studyId) {
    const res = await fetch(`${API_BASE}/analysis/study/${studyId}/performance`)
    if (!res.ok) throw new Error(`Failed to fetch study performance: ${res.status}`)
    return res.json()
}

export async function fetchStudyQuestionnaires(studyId) {
    const res = await fetch(`${API_BASE}/analysis/study/${studyId}/questionnaires`)
    if (!res.ok) throw new Error(`Failed to fetch study questionnaires: ${res.status}`)
    return res.json()
}

export async function fetchStudyEyeTracking(studyId) {
    const res = await fetch(`${API_BASE}/analysis/study/${studyId}/eyetracking`)
    if (!res.ok) throw new Error(`Failed to fetch study eye tracking: ${res.status}`)
    return res.json()
}
