import { useEffect, useState } from "react";
import { fetchExperimentEyeTrackingPhases } from "../services/eyeTrackingService";

export function useEyeTrackingPhases(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentEyeTrackingPhases(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
