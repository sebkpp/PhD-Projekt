export function generateParticipantUrl(study_id, experimentId, participant_id, trial_id, slot, status) {
    if (status) {
        // Wenn status gesetzt ist, gib eine alternative URL zurück
        return `${window.location.origin}/study/${study_id}/experiment/${experimentId}/questionnaire?slot=${slot}&participant=${participant_id}&trial=${trial_id}`;
    } else {
        // Standard-URL, wenn status nicht gesetzt ist
        return `${window.location.origin}/study/${study_id}/experiment/${experimentId}/questionnaireStart?slot=${slot}&participant=${participant_id}&trial=${trial_id}`;
    }
}