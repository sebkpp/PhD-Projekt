export async function fetchTrials(experimentId) {
    const res = await fetch(`/api/experiments/${experimentId}/trials`)
    if (!res.ok) throw new Error("Fehler beim Laden der Trials")
    return await res.json()
}

export async function fetchStimuli() {
    const res = await fetch('/api/stimuli')
    if (!res.ok) throw new Error("Fehler beim Laden der Stimuli")
    return await res.json()
}

export async function fetchHandovers(trialId) {
    const res = await fetch(`/api/trials/${trialId}/handovers`)
    if (!res.ok) throw new Error("Fehler beim Laden der Handovers")
    return await res.json()
}

export async function getParticipantsForExperiment(experimentId) {
    const response = await fetch(`/api/participants/experiment/${experimentId}`)
    if (!response.ok) throw new Error('Fehler beim Laden der Teilnehmer')
    return await response.json()
}

export async function startTrial(trialId) {
    const response = await fetch(`/api/trial/${trialId}/start`, {
        method: 'POST'
    });

    if (!response.ok) {
        throw new Error('Trial konnte nicht gestartet werden');
    }

    return response.json();
}

export async function endTrial(trialId) {
    const response = await fetch(`/api/trial/${trialId}/end`, {
        method: 'POST',
    });

    if (!response.ok) {
        throw new Error('Trial konnte nicht beendet werden');
    }

    return response.json();
}

export async function areAllQuestionnairesInTrialDone(participants, trialId) {
    if (!trialId || !participants?.length) return true;
    const participantIds = participants.map(p => p.participant_id);
    const results = await Promise.all(
        participantIds.map(pid =>
            fetch(`/api/questionnaires/trial_done?participant=${pid}&trial=${trialId}`)
                .then(res => res.json())
        )
    );
    return results.every(r => r.allDone);
}

export async function areAllQuestionnairesDone(participantId, experiment) {
    const response = await fetch(`/api/questionnaires/done?participant=${participantId}&experiment=${experiment}`)
    const data = await response.json()
    return data.allDone
}

export async function loadAndSortTrials(experimentId) {
    const data = await fetchTrials(experimentId)
    if (!Array.isArray(data)) throw new Error("Keine gültigen Trial-Daten empfangen")
    return data.slice().sort((a, b) => a.trial_number - b.trial_number)
}

export async function loadStimulusMap() {
    const data = await fetchStimuli()
    const map = {}
    data.forEach(stim => { map[stim.id] = stim.name })
    return map
}

export async function getTrialById(trialId) {
    const res = await fetch(`/api/trial/${trialId}`)
    if (!res.ok) throw new Error("Fehler beim Laden des Trials")
    return await res.json()
}