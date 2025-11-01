import ParticipantCard from "@/features/configuration/components/ParticipantConfigCard";

export default function TrialConfig({ study_configs, onChange }) {


    return (
        <div className="flex flex-col gap-4">
            {[0, 1].map((id) => (
                <ParticipantCard
                    key={id}
                    onChange={newData => onChange(id, newData)}
                    disabled={false}
                />
            ))}
        </div>
    );
}