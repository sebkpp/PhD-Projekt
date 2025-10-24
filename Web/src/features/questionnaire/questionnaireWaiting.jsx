import {useSearchParams, useNavigate, useParams} from 'react-router-dom'
import { useQuestionnaireAvailability } from '@/features/questionnaire/hooks/useQuestionnaireAvailability.js'
import { useSyncTrialIdInUrl } from '@/features/questionnaire/hooks/useSyncTrialIdInUrl.js'

function WaitingContent(){
    return (
        <>
            <p className="text-lg text-gray-400 max-w-md mb-6">
                Bitte warte, bis der aktuelle Trial beendet ist und die Fragebögen freigeschaltet werden.
            </p>
            <div className="animate-pulse text-accent text-4xl">⏳</div>
        </>
    )
}

function ReadyContent({ onContinue }) {
    return (
        <>
            <p className="text-lg text-accent font-semibold max-w-md mb-4">
                Die Fragebögen sind jetzt bereit.
            </p>
            <button
                onClick={onContinue}
                className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition"
            >
                Weiter zum nächsten Fragebogen 🚀
            </button>
        </>
    )
}

export default function QuestionnaireWaiting() {
    const { studyId, experimentId } = useParams()
    const [searchParams] = useSearchParams()
    const participantId = searchParams.get('participant')
    const slot = searchParams.get('slot')
    const trialId = searchParams.get('trial')

    const navigate = useNavigate()
    console.log("QuestionnaireWaiting for participant:", participantId, "in slot:", slot)
    const {trialId:currentTrialId, ready, error } = useQuestionnaireAvailability({studyId, experimentId, participantId, trialId })
    useSyncTrialIdInUrl(currentTrialId);

    const handleContinue = () => {
        if (ready) {
            navigate(
                `/study/${studyId}/experiment/${experimentId}/questionnaireForm?slot=${slot}&participant=${participantId}&trial=${currentTrialId}`
            )
        }
    }

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6 text-center">
            {!ready
                ? <WaitingContent />
                : <ReadyContent onContinue={handleContinue} />
            }
            {error && <p className="text-red-500 mt-4">{error}</p>}
        </div>
    )
}
