export async function getExperimentQuestionnaires(experimentId, participantId) {
    const response = await fetch(`/api/experiments/${experimentId}/participants/${participantId}/questionnaires`)
    console.log("response", response)

    if (!response.ok) throw new Error('Fehler beim Laden der Fragebögen')
    const data = await response.json()
    return data
}

export async function getStudyQuestionnaires(study_id) {
    const response = await fetch(`/api/questionnaires/study/${study_id}`)
    if (!response.ok) throw new Error('Fehler beim Laden der Fragebögen')
    const data = await response.json()
    return data
}

export async function getTrialsForExperiment(experimentId) {
    const response = await fetch(`/api/experiments/${experimentId}/trials`)
    if (!response.ok) throw new Error('Fehler beim Laden der Trials')
    const data = await response.json()
    return data
}

export async function areAllQuestionnairesDone({ participantId, experimentId }) {
    const response = await fetch(`/api/questionnaires/done?participant=${participantId}&experiment=${experimentId}`)
    if (!response.ok) throw new Error('Fehler beim Prüfen des Fragebogen-Status')
    const data = await response.json()
    return data.allDone
}

export async function getNextQuestionnaireRoute({ participantId, studyId, experimentId, trialId, slot }) {
    const allDone = await areAllQuestionnairesDone({ participantId, experimentId })
    console.log("allDone", allDone)
    if (allDone) {
        return '/questionnaire/closing'
    } else {
        return `/study/${studyId}/experiment/${experimentId}/questionnaire?slot=${slot}&participant=${participantId}&trial=${trialId}`
    }
}