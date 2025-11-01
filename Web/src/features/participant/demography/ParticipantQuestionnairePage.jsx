import ParticipantQuestionnaireForm from './ParticipantQuestionnaireForm.jsx'
import { useParticipantQuestionnaire } from './useParticipantQuestionnaire.js'
import {useParams} from "react-router-dom";

export default function ParticipantQuestionnairePage() {
    const params = new URLSearchParams(window.location.search)
    const {studyId, experimentId} = useParams()
    const trial_id = params.get('trial')
    const slot = params.get('slot')

    console.log("ParticipantQuestionnairePage for trial:", trial_id, "in slot:", slot)

    const questionnaire = useParticipantQuestionnaire(studyId, experimentId, trial_id , slot )

    return <ParticipantQuestionnaireForm {...questionnaire} onSubmit={questionnaire.handleSubmit} />

}
