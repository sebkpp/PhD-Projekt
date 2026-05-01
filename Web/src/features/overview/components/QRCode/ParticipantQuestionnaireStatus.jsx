import QRCodeCard from '../../../shared/components/QRCodeCard.jsx'
import { useQuestionnaireStartQrUrl } from './useQuestionnaireStartQrUrl'
import { useQuestionnaireCompletionStatus } from './useQuestionnaireCompletionStatus'
import { useStudyQuestionnaires } from '@/features/questionnaire/hooks/useStudyQuestionnaires.js'

export default function ParticipantQuestionnaireStatus({ experimentId, slot, status, trialId }) {
    const participant = status?.participants?.find((p) => p.slot === slot)
    const participant_id = participant?.participant_id
    const submitted = participant?.submitted

    // Hole die Fragebögen für das Experiment
    const { questionnaires, questionnaire_loading, error } = useStudyQuestionnaires(experimentId)
    const questionnaireNames = questionnaires.map(q => q.name)

    const { completedCount, totalCount, loading } = useQuestionnaireCompletionStatus(
        experimentId,
        participant_id,
        trialId,
        questionnaireNames
    )

    const url = useQuestionnaireStartQrUrl(experimentId, slot, participant_id, trialId)

    return (
        <div className="flex-1 min-w-[180px] max-w-[300px] basis-0 bg-gray-800 rounded-lg border border-border p-4 flex flex-col items-center">
            <QRCodeCard
                url={url}
                slot={slot}
                participant_id={participant_id}
            />
            <div className="mt-2 text-sm text-gray-300">
                {loading
                    ? "Lade Status..."
                    : `Fragebögen: ${completedCount} / ${totalCount} ausgefüllt`}
            </div>
        </div>
    )
}
