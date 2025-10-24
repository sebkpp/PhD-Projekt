import StimulusIcon from "@/features/study/utils/stimuliUtils.jsx";

export default function TrialStimuliBox({ title, trialNumber, slots, highlight = false }) {
    if (!slots) return null
    return (
        <div className={`space-y-4 rounded-xl p-6 shadow-md border
            ${highlight
            ? 'bg-blue-100 border-blue-200 dark:bg-blue-950 dark:border-blue-700'
            : 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
        }`}>
            <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-900 dark:text-gray-100">
                {title} <span className="text-base text-gray-400 dark:text-gray-400">({trialNumber})</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {slots.map((slot) => (
                    <StimulusCard key={slot.trial_slot_id} slotNumber={slot.slot} stimuli={slot.stimuli} />
                ))}
            </div>
        </div>
    )
}

function StimulusCard({ slotNumber, stimuli }) {
    return (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow hover:shadow-lg transition p-5 border border-gray-100 dark:border-gray-700 flex flex-col gap-2">
            <div className="font-semibold text-lg mb-2 text-accent dark:text-accent-light">
                Proband Slot {slotNumber}
            </div>
            <ul className="text-sm space-y-2">
                {stimuli.map((stimulus) => (
                    <li key={stimulus.stimulus_id} className="flex items-center gap-2">
                        <StimulusIcon type={stimulus.stimulus_type} />
                        <span className="font-medium text-gray-500 dark:text-gray-300">{stimulus.name}</span>
                    </li>
                ))}
            </ul>
        </div>
    )
}