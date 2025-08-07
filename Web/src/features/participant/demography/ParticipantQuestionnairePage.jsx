import ParticipantQuestionnaireForm from './ParticipantQuestionnaireForm.jsx'
import { useParticipantQuestionnaire } from './useParticipantQuestionnaire.js'

export default function ParticipantQuestionnairePage() {
    const params = new URLSearchParams(window.location.search)
    const experimentId = parseInt(params.get('experiment'))
    const slot = params.get('slot')

    const questionnaire = useParticipantQuestionnaire(experimentId, slot)

    return <ParticipantQuestionnaireForm {...questionnaire} onSubmit={questionnaire.handleSubmit} />

}
