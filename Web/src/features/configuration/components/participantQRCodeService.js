export function generateParticipantUrl(experimentId, slot) {
    return `${window.location.origin}/participant/start?experiment=${experimentId}&slot=${slot}`
}