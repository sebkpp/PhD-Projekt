import ParticipantQRCodeCard from './ParticipantQRCodeCard'
import { useParticipantQrUrl } from './useParticipantQRCode'

export default function ParticipantDemographyStatus({ experiment_id, slot, status }) {
    const url = useParticipantQrUrl(experiment_id, slot)

    const slotStatus = status?.[slot]
    const submitted = slotStatus?.submitted
    const participant_id = slotStatus?.participant_id

    return (
        <div className="min-w-[260px] p-4 bg-gray-800 rounded-lg border border-border flex flex-col items-center">
            <ParticipantQRCodeCard url={url} slot={slot} />
            <div className="mt-3 text-sm text-center">
                <strong>Proband {slot}</strong>:{' '}
                {submitted ? (
                    <span className="text-green-400">
                        ✅ Abgeschickt
                        {participant_id && (
                            <span className="text-gray-400 ml-1">(ID: {participant_id})</span>
                        )}
                    </span>
                ) : (
                    <span className="text-yellow-300">❌ Noch offen</span>
                )}
            </div>
        </div>
    )
}
