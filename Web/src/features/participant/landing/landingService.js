export async function fetchActiveQuestionnaire(experimentId, slot) {
    const res = await fetch(`/api/active-questionnaire?experiment=${experimentId}&slot=${slot}`)
    if (!res.ok) throw new Error('Fehler beim Abrufen des aktiven Fragebogens')
    return await res.json()
}