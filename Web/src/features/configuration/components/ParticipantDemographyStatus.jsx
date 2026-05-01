import QRCodeCard from '../../shared/components/QRCodeCard.jsx'
import { useParticipantQrUrl } from '../../overview/hooks/useParticipantQRCode.js'
import {getParticipantSubmissionStatus} from "@/features/participant/demography/participantQuestionnaireService.js";
import {useEffect, useRef, useState} from "react";
import {
    useQuestionnaireCompletionStatus
} from "@/features/overview/components/QRCode/useQuestionnaireCompletionStatus.js";
import {useStudyQuestionnaires} from "@/features/questionnaire/hooks/useStudyQuestionnaires.js";
import {getTrialsForExperiment} from "@/features/questionnaire/service/questionnaireFlowService.js";
import {getTrialById} from "@/features/overview/services/trialOverviewService.js";

export default function ParticipantDemographyStatus({ study_id,  experiment_id, trial_id, slot }) {
    const [status, setStatus] = useState(null)
    const [questionnaireStatus, setQuestionnaireStatus] = useState(null)
    const intervalRef = useRef(null)

    useEffect(() => {
        async function fetchStatus() {
            const result = await getParticipantSubmissionStatus({experiment_id, slot})
            if (result && Object.keys(result).length > 0) {
                setStatus(result)
                if (intervalRef.current) {
                    clearInterval(intervalRef.current)
                    intervalRef.current = null
                }
            } else {
                setStatus(null)
            }
        }

        fetchStatus()
        intervalRef.current = setInterval(fetchStatus, 2000)

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, [experiment_id, slot])


    const participant_id = status ? Object.keys(status)[0] : null
    const {questionnaires, questionnaire_loading, error} = useStudyQuestionnaires(study_id)
    const questionnaireNames = questionnaires?.map(q => q.name) || [];
    const [isTrialFinished, setIsTrialFinished] = useState(false);

    const { completedCount, totalCount, loading } = useQuestionnaireCompletionStatus(
        experiment_id,
        participant_id,
        trial_id,
        questionnaireNames
    )

    useEffect(() => {
        if (!trial_id) return;
        let interval = setInterval(async () => {
            //const trials = await getTrialsForExperiment(experiment_id);
            //const currentTrial = trials.find(t => t.trial_id == trial_id);
            const currentTrial = await getTrialById(trial_id);
            if (currentTrial?.is_finished) {
                setIsTrialFinished(true);
                clearInterval(interval);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [experiment_id, trial_id]);

    const url = useParticipantQrUrl(study_id, experiment_id, participant_id, trial_id, slot, status)

    return (
        <div className="min-w-[260px] p-4 bg-gray-800 rounded-lg border border-border flex flex-col items-center">
            <QRCodeCard
                url={url}
                slot={slot}
                participant_id={participant_id}
            />
            <div className="mt-3 text-sm text-center">
                <strong>Status</strong>:{' '}
                {!trial_id ? (
                    status ? (
                        <span className="text-green-400">
                ✅ Demographie-Fragebogen abgeschickt
            </span>
                    ) : (
                        <span className="text-yellow-300">❌ Noch nicht ausgefüllt</span>
                    )
                ) : !participant_id ? (
                    <span className="text-yellow-300">❌ Noch nicht ausgefüllt</span>
                ) : isTrialFinished ? (
                    loading ? (
                        <span className="text-gray-400">Fragebogen-Status wird geladen...</span>
                    ) : (
                        <span>
                {completedCount} / {totalCount} Fragebögen beantwortet
            </span>
                    )
                ) : status ? (
                    <span className="text-green-400">
            ✅ Demographie-Fragebogen abgeschickt
        </span>
                ) : (
                    <span className="text-yellow-300">❌ Noch nicht ausgefüllt</span>
                )}
            </div>
        </div>
    )
}
