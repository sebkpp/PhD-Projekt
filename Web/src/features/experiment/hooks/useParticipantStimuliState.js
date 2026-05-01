import { useEffect, useState } from "react";
import { getActiveTypes, getSelectedStimuli } from "@/features/experiment/services/participantStimuliService.js";

export function useParticipantStimuliState(config) {
    const [activeTypes, setActiveTypes] = useState(() => getActiveTypes(config.active_stimuli));
    const [selectedStimuli, setSelectedStimuli] = useState(() => getSelectedStimuli(config.active_stimuli));

    useEffect(() => {
        setActiveTypes(getActiveTypes(config.active_stimuli));
        setSelectedStimuli(getSelectedStimuli(config.active_stimuli));
    }, [config.active_stimuli]);

    return { activeTypes, setActiveTypes, selectedStimuli, setSelectedStimuli };
}