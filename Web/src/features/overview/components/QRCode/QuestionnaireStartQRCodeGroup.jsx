import ParticipantQuestionnaireStatus from './ParticipantQuestionnaireStatus'

export default function QuestionnaireStartQrCodeGroup({ experimentId, status, trialId }) {
    return (
        <div className="border border-border rounded-xl p-6 bg-gray-900 w-full">
            <h2 className="text-xl font-semibold mb-4 text-center">
                Fragebogen-Link für die Probanden (nach Demographie)
            </h2>
            <div className="flex justify-center gap-4 w-full">
                {[1, 2].map((slot) => (
                    <ParticipantQuestionnaireStatus
                        key={slot}
                        experimentId={experimentId}
                        slot={slot}
                        status={status}
                        trialId={trialId}
                    />
                ))}
            </div>
        </div>
    )
}
