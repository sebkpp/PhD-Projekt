// src/features/experiment/hooks/useParticipantStimuliHandlers.js
import { useCallback } from "react";
import { buildConfig } from "@/features/experiment/services/participantStimuliService.js";

export function useParticipantStimuliHandlers({ state, slot, stimuli, options, onChange }) {
    const { activeTypes, setActiveTypes, selectedStimuli, setSelectedStimuli } = state;

    const handleCheckboxChange = useCallback((stimulusTypeId) => {
        const newActive = activeTypes.includes(stimulusTypeId)
            ? activeTypes.filter(id => id !== stimulusTypeId)
            : [...activeTypes, stimulusTypeId];
        setActiveTypes(newActive);
        onChange && onChange(buildConfig(slot, newActive, selectedStimuli, stimuli, options));
    }, [activeTypes, selectedStimuli, stimuli, options, slot, setActiveTypes, onChange]);

    const handleSelectChange = useCallback((stimulusTypeId, value) => {
        const newSelected = { ...selectedStimuli, [stimulusTypeId]: value };
        setSelectedStimuli(newSelected);
        onChange && onChange(buildConfig(slot, activeTypes, newSelected, stimuli, options));
    }, [activeTypes, selectedStimuli, stimuli, options, slot, setSelectedStimuli, onChange]);

    return { handleCheckboxChange, handleSelectChange };
}