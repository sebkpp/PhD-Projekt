import QuestionnaireQRCode from './QuestionnaireQRCode.jsx'

export default function QuestionnaireQrGroup({ experimentId, status }) {
    const getStatusLabel = (slot) => {
        const slotStatus = status?.[slot]
        if (!slotStatus) return null

        const { submitted, participant_id } = slotStatus
        return submitted ? (
            <span className="text-green-400">
                ✅ Abgeschickt
                {participant_id && (
                    <span className="text-gray-400 ml-1">(ID: {participant_id})</span>
                )}
            </span>
        ) : (
            <span className="text-yellow-300">❌ Noch offen</span>
        )
    }

    return (
        <div className="border border-border rounded-xl p-6 bg-gray-900 w-full">
            <h2 className="text-xl font-semibold mb-4 text-center">
                Fragebogen-Link für die Probanden
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map((slot) => (
                    <div
                        key={slot}
                        className="min-w-[260px] p-4 bg-gray-800 rounded-lg border border-border flex flex-col items-center"
                    >
                        <QuestionnaireQRCode experimentId={experimentId} slot={slot} />
                        <div className="mt-3 text-sm">
                            <strong>Proband {slot}</strong>: {getStatusLabel(slot)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
