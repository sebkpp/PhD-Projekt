export async function fetchExperimentById(experimentId) {
    if (!experimentId) throw new Error("experimentId ist erforderlich");
    const response = await fetch(`/api/experiments/${experimentId}`);
    if (!response.ok) {
        throw new Error("Fehler beim Laden des Experiments");
    }
    return await response.json();
}

export async function fetchQuestionnaireResponsesById(experimentId) {
    if (!experimentId) throw new Error("experimentId ist erforderlich");
    const response = await fetch(`/api/experiments/${experimentId}/questionnaire-responses`);
    if (!response.ok) {
        throw new Error("Fehler beim Laden der Questionnaire-Responses");
    }
    return await response.json();
}

export async function fetchHandoversByExperimentId(experimentId) {
    if (!experimentId) throw new Error("experimentId ist erforderlich");
    const response = await fetch(`/api/experiments/${experimentId}/handovers`);
    if (!response.ok) {
        throw new Error("Fehler beim Laden der Handovers");
    }
    return await response.json();
}
