export function validateExperimentTrialConfigs(trialConfigs, trialCount=1, slotCount = 2) {
    const errors = [];
    // Für alle erwarteten Trials prüfen
    for (let trialIndex = 0; trialIndex < trialCount; trialIndex++) {
        const trialKey = `Trial ${trialIndex + 1}`;
        const trial = trialConfigs[trialKey];
        for (let slot = 1; slot <= slotCount; slot++) {
            const slotKey = `Slot ${slot}`;
            const slotObj = trial?.[slotKey];
            if (!slotObj || !slotObj.active_stimuli || Object.keys(slotObj.active_stimuli).length === 0) {
                errors.push({
                    trialIndex,
                    slotKey,
                    field: "stimuli",
                    message: `Trial ${trialIndex + 1}, ${slotKey}: Es muss mindestens ein Stimulus-Typ aktiviert sein.`
                });
                continue;
            }
            Object.values(slotObj.active_stimuli).forEach(s => {
                const typeId = typeof s.stimuli_type_id === "string" ? s.stimuli_type_id : String(s.stimuli_type_id || "");
                if (!s.selected_stimuli_id || s.selected_stimuli_id === "") {
                    errors.push({
                        trialIndex,
                        slotKey,
                        field: `stimuli.${typeId}`,
                        message: `Trial ${trialIndex + 1}, ${slotKey}: Für aktivierten Stimulus "${typeId.toUpperCase()}" fehlt die spezifische Auswahl.`
                    });
                }
            });
        }
    }
    return errors;
}