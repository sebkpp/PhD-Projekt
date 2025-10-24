import {useParams, useSearchParams} from 'react-router-dom'
import QuestionnaireForm from './QuestionnaireForm'
import { useStudyQuestionnaires } from '@/features/questionnaire/hooks/useStudyQuestionnaires.js'
import {useHandleAllDone} from "@/features/questionnaire/hooks/useHandleAllDone.js";
import {useQuestionnaireNavigator} from "@/features/questionnaire/hooks/useQuestionnaireNavigator.js";
import {useEffect, useState} from "react";
import {getParticipantSubmissionStatus} from "@/features/participant/demography/participantQuestionnaireService.js"; // Dein Demographie-Fragebogen

export default function QuestionnaireRouter() {
    const [searchParams] = useSearchParams()
    const { studyId, experimentId } = useParams()
    const slot = searchParams.get('slot')
    const trial_id = searchParams.get('trial')

    const [status, setStatus] = useState(false);

    useEffect(() => {
        async function fetchStatus() {
            const result = await getParticipantSubmissionStatus({experiment_id: experimentId, slot})
            if (result && Object.keys(result).length > 0) {
                setStatus(result);
            } else {
                setStatus(null);
            }
        }
        fetchStatus()
    }, [experimentId, slot])

    const participant_id = status ? parseInt(Object.keys(status)[0]) : null

    const { questionnaires, loading, error } = useStudyQuestionnaires(studyId)
    const handleAllDone = useHandleAllDone({ participantId: participant_id, studyId, experimentId, trialId: trial_id, slot })
    const { currentIndex, resetSignal, handleNext } = useQuestionnaireNavigator(questionnaires.length, handleAllDone)
    const currentQuestionnaire = questionnaires[currentIndex]

    return (
        <div className="min-h-screen bg-background text-foreground p-8 flex flex-col items-center">
            <div className="ml-16 w-full max-w-3xl flex items-center mb-6">
                <h2 className="text-xl font-semibold mr-8">
                    {currentQuestionnaire?.name} - Proband {slot}
                </h2>
                <span className="text-gray-400 whitespace-nowrap">
                    Fragebogen {currentIndex + 1} von {questionnaires.length}
                </span>
            </div>
            <QuestionnaireForm
                questionnaire={currentQuestionnaire}
                participantId={participant_id}
                trialId={trial_id}
                onNext={handleNext}
                resetSignal={resetSignal}
            />
        </div>
    )
}
