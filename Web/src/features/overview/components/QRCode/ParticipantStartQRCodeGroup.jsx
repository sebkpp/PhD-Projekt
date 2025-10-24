import ParticipantDemographyStatus from '../../../configuration/components/ParticipantDemographyStatus.jsx'

export default function QuestionnaireQrGroup({study_id, experiment_id, status, trialId }) {
    return (
        <div className="border border-border rounded-xl p-6 bg-gray-900 w-full">
            <h2 className="text-xl font-semibold mb-4 text-center">
                Probanden Registierung
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map((slot) => (
                    <ParticipantDemographyStatus
                        key={slot}
                        study_id={study_id}
                        experiment_id={experiment_id}
                        trial_id={trialId}
                        slot={slot}
                        status={status}
                    />
                ))}
            </div>
        </div>
    )
}
