export function generateQuestionnaireStartUrl(experimentId, slot, participantId, trial_id) {
    return `${window.location.origin}/participant/waiting?experiment=${experimentId}&slot=${slot}&participant=${participantId}&trial_id=${trial_id}`
}
