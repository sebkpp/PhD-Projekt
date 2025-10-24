import TrialParticipantConfigCard from './TrialParticipantConfigTile';
import {useEffect, useMemo, useState} from "react";

function TrialParticipantsTile({ allowedStimuli, onChange, trial_number, configs, validationErrors = [], showValidation }) {
    const stimuli = useMemo(() => allowedStimuli || [], [allowedStimuli]);

    function handleConfigChange(slot, config) {
        const slotKey = `Slot ${slot}`;
        const newConfigs = { ...configs, [slotKey]: config[slotKey] };
        onChange && onChange(newConfigs);
    }

    return (
        <div className="flex flex-col gap-8">
            <TrialParticipantConfigCard
                allowedStimuli={stimuli}
                onChange={config => handleConfigChange(1, config)}
                label="Proband 1"
                slot={1}
                trial_number={trial_number}
                config={configs["Slot 1"] || {}}
                validationErrors={validationErrors.filter(e => e.slotKey === "Slot 1")}
                showValidation={showValidation}
            />
            <TrialParticipantConfigCard
                allowedStimuli={stimuli}
                onChange={config => handleConfigChange(2, config)}
                label="Proband 2"
                slot={2}
                trial_number={trial_number}
                config={configs["Slot 2"] || {}}
                validationErrors={validationErrors.filter(e => e.slotKey === "Slot 2")}
                showValidation={showValidation}
            />
        </div>
    );
}

export default TrialParticipantsTile;