export async function getAllQuestionnaires() {
    const res = await fetch('/api/questionnaires')
    if (!res.ok) {
        throw new Error('Fehler beim Laden der Fragebögen')
    }
    const json = await res.json()
    return json.data
}

export async function saveSelectedQuestionnaires(experimentId, selectedQuestionnaires) {
    const res = await fetch(`/api/experiment/${experimentId}/questionnaires`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            questionnaires: selectedQuestionnaires.map((q, index) => ({
                questionnaire_id: q.questionnaire_id,
                order: index
            }))
        })
    })

    if (!res.ok) {
        const text = await res.text()
        throw new Error(`Fehler beim Speichern der Fragebögen: ${text}`)
    }

    return res.json()
}