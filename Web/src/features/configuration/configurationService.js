export async function fetchParticipantStatus(experimentId, participantId) {
    const res = await fetch(`/api/participants/status/${participantId}?experiment_id=${experimentId}`)
    if (!res.ok) throw new Error(`Fehler beim Laden von Status P${participantId}`)
    return await res.json()
}

export async function submitTrialConfiguration(experimentId, trialConfigs, status) {
    const payload = {
        experiment_id: Number(experimentId),
        trials: trialConfigs.map((cfg, index) => ({
            trial_number: index + 1,
            participants: {
                1: {
                    ...cfg[1],
                    participant_id: Number(status[1]?.participant_id),
                    avatar: Number(cfg[1].avatar),
                    selectedStimuli: Object.fromEntries(
                        Object.entries(cfg[1].selectedStimuli || {}).map(([key, val]) => [key, Number(val)])
                    )
                },
                2: {
                    ...cfg[2],
                    participant_id: Number(status[2]?.participant_id),
                    avatar: Number(cfg[2].avatar),
                    selectedStimuli: Object.fromEntries(
                        Object.entries(cfg[2].selectedStimuli || {}).map(([key, val]) => [key, Number(val)])
                    )
                }
            }
        }))
    }

    console.log(payload)
    const res = await fetch(`/api/experiments/${experimentId}/trials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })

    if (!res.ok) throw new Error('Fehler beim Speichern der Trials')
}

export async function getConnectionStatus() {
    const res = await fetch('/api/participants/connection_status')
    if (!res.ok) throw new Error('Verbindungsstatus konnte nicht geladen werden')
    return await res.json()
}