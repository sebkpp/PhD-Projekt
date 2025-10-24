import { useState, useMemo } from "react";
import { validateExperimentTrialConfigs } from "@/features/experiment/validation/validateExperimentTrialConfigs.js";

export function useValidation(trialConfigs, trialCount) {
    const [showError, setShowError] = useState(false);
    const [validationErrors, setValidationErrors] = useState([]);

    const errors = useMemo(
        () => validateExperimentTrialConfigs(trialConfigs, trialCount),
        [trialConfigs, trialCount]
    );

    function handleSaveExperiment() {
        setValidationErrors(errors);
        if (errors.length > 0) {
            setShowError(true);
            return false;
        }
        setShowError(false);
        return true;
    }

    return { errors, showError, setShowError, validationErrors, handleSaveExperiment };
}