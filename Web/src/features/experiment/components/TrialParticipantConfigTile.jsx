import {useStimuliOptions} from "@/features/experiment/hooks/useStimuliOptions.js";
import { useParticipantStimuliState } from "@/features/experiment/hooks/useParticipantStimuliState.js";
import {useParticipantStimuliHandlers} from "@/features/experiment/hooks/useParticipantStimuliHandlers.js";

export default function TrialParticipantConfigTile({ allowedStimuli, onChange, label, slot, trial_number, config, validationErrors = [], showValidation  }) {
    const stimuli = allowedStimuli || [];
    const { filtered_stimuli_options, loading, error } = useStimuliOptions();
    const state = useParticipantStimuliState(config);

    const props = {
        slot,
        stimuli,
        options: filtered_stimuli_options,
        onChange
    };

    const { handleCheckboxChange, handleSelectChange } = useParticipantStimuliHandlers({ state, ...props });
    const hasNoneActiveError = showValidation && validationErrors.some(e => e.slotKey === `Slot ${slot}` && e.field === "stimuli");


    return (
        <div className={
            "bg-gray-800 p-6 rounded-xl border shadow-lg flex flex-col gap-6 min-w-[320px] " +
            (hasNoneActiveError ? "border-red-500" : "border-gray-700")
        }>
            <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold text-lg text-gray-100">{label}</h2>
                <span className="text-xs text-gray-400">
        Slot {slot} · Trial {trial_number + 1}
      </span>
            </div>
            <div className="flex flex-col gap-6">
                {stimuli.map(stimulus => {
                    const stimulusTypeId = stimulus.stimuli_type_id;
                    const specificStimuli =
                        filtered_stimuli_options?.[stimulus.name] || [];
                    const isInvalid = showValidation && validationErrors.some(e =>
                        e.slotKey === `Slot ${slot}` && e.field === `stimuli.${stimulusTypeId}`
                    );

                    return (
                        <div
                            key={stimulusTypeId}
                            className={
                                `flex flex-row items-center gap-3 bg-gray-700 p-3 rounded-lg border min-w-[180px] w-full transition-colors duration-200 hover:border-gray-400 ` +
                                (isInvalid ? "border-red-500" : "border-gray-600")
                            }
                        >
                            <label className="flex items-center gap-4 font-medium min-w-[120px]">
                                <input
                                    type="checkbox"
                                    checked={state.activeTypes.includes(stimulusTypeId)}
                                    onChange={() => handleCheckboxChange(stimulusTypeId)}
                                    className="w-5 h-5 accent-indigo-500 rounded focus:ring-2 focus:ring-indigo-400 transition-all"
                                />
                                {stimulus.name}
                            </label>

                            {/* fixierter Bereich für Dropdown, Höhe bleibt stabil */}
                            <div className="flex-1 min-w-[160px] ml-8 flex items-center h-[32px]">
                                {state.activeTypes.includes(stimulusTypeId) ? (
                                    <select
                                        className="bg-gray-900 border border-gray-500 rounded px-2 py-2 text-sm w-full"
                                        value={state.selectedStimuli[stimulusTypeId] || ""}
                                        onChange={e => handleSelectChange(stimulusTypeId, e.target.value)}
                                    >
                                        <option value="">Stimulus wählen</option>
                                        {specificStimuli.map(s => (
                                            <option key={s.value} value={s.value}>{s.label}</option>
                                        ))}
                                    </select>
                                ) : (
                                    // Platzhalter, wenn nicht aktiv
                                    <div className="h-[30px]"></div>
                                )}
                            </div>
                        </div>

                    );
                })}
            </div>
        </div>
    );
}