export async function createParticipant(data) {
    const res = await fetch('/api/participants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })

    if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`Fehler beim Erstellen des Teilnehmers: ${errorText}`)
    }

    return await res.json()
}

export async function submitParticipant({ slot, experiment_id, participant_id }) {
    const res = await fetch('/api/participants/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot, experiment_id, participant_id }),
    })

    if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`Fehler beim Absenden der Teilnehmer-Submit-Daten: ${errorText}`)
    }

    return await res.json()
}
