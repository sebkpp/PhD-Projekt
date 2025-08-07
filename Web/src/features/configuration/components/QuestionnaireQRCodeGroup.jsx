import ParticipantDemographyStatus from './ParticipantDemographyStatus.jsx'

export default function QuestionnaireQrGroup({ experiment_id, status }) {
    return (
        <div className="border border-border rounded-xl p-6 bg-gray-900 w-full">
            <h2 className="text-xl font-semibold mb-4 text-center">
                Fragebogen-Link für die Probanden
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map((slot) => (
                    <ParticipantDemographyStatus
                        key={slot}
                        experiment_id={experiment_id}
                        slot={slot}
                        status={status}
                    />
                ))}
            </div>
        </div>
    )
}
