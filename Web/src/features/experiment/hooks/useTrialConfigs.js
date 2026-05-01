import { useState } from "react";

export function useTrialConfigs(activeIndex) {
    const [trialConfigs, setTrialConfigs] = useState({});

    function handleStimuliChange(updatedSlotConfig) {
        const trialKey = `Trial ${activeIndex + 1}`;
        setTrialConfigs(prev => ({
            ...prev,
            [trialKey]: {
                ...prev[trialKey],
                ...updatedSlotConfig
            }
        }));
    }

    return { trialConfigs, setTrialConfigs, handleStimuliChange };
}