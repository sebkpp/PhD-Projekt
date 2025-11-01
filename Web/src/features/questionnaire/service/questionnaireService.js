export async function submitQuestionnaire(participantId, trialId, questionnaireName, responses) {

    const response = await fetch('/api/submit-questionnaire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            participant_id: participantId,
            trial_id: trialId,
            questionnaire_name: questionnaireName,
            responses: responses
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Fehler beim Absenden des Fragebogens');
    }

    return response.json();
}
