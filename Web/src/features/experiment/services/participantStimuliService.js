// src/features/experiment/services/participantStimuliService.js
export function getActiveTypes(active_stimuli) {
    if (!active_stimuli) return [];
    return Object.values(active_stimuli).map(s => s.stimuli_type_id);
}

export function getSelectedStimuli(active_stimuli) {
    if (!active_stimuli) return {};
    return Object.values(active_stimuli).reduce((acc, s) => {
        acc[s.stimuli_type_id] = s.selected_stimuli_id;
        return acc;
    }, {});
}

export function buildConfig(slot, activeTypes, selectedStimuli, stimuli, options) {
    const activeStimuli = {};
    activeTypes.forEach(typeId => {
        const typeObj = stimuli.find(s => s.stimuli_type_id === typeId);
        const specificStimuli = options?.[stimuli.name] || [];
        const selectedId = selectedStimuli[typeId];
        const selectedObj = specificStimuli.find(s => String(s.value) === String(selectedId));

        activeStimuli[typeObj?.name || typeId] = {
            stimuli_type_id: typeId,
            selected_stimuli_id: selectedId || null,
            selected_stimuli_name: selectedObj?.label || ""
        };
    });

    return {
        [`Slot ${slot}`]: {
            active_stimuli: activeStimuli,
        }
    };
}