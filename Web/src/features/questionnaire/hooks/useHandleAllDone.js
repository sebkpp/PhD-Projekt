import { useNavigate } from 'react-router-dom'
import {getNextQuestionnaireRoute, getTrialsForExperiment} from '../service/questionnaireFlowService.js'

export function useHandleAllDone({ participantId, studyId, experimentId, trialId, slot }) {
    const navigate = useNavigate()

    return async function handleAllDone() {
        try {
            const trials = await getTrialsForExperiment(experimentId)
            const currentTrial = trials.find(t => t.trial_id == trialId)
            const nextTrial = trials
                .filter(t => t.trial_number > currentTrial.trial_number && !t.is_finished)
                .sort((a, b) => a.trial_number - b.trial_number)[0]

            if (nextTrial) {
                navigate(`/study/${studyId}/experiment/${experimentId}/questionnaire?slot=${slot}&participant=${participantId}&trial=${nextTrial.trial_id}`)
            } else {
                navigate('/questionnaire/closing')
            }

            //const route = await getNextQuestionnaireRoute({ participantId, studyId, experimentId, trialId, slot })
            //navigate(route)
        } catch (err) {
            alert('Fehler beim Prüfen des Fragebogen-Status: ' + err.message)
            navigate('/questionnaire/closing')
        }
    }
}