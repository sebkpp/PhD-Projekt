import { useEffect, useState } from "react";
import { fetchExperimentEyeTrackingTransitions } from "../services/eyeTrackingService";

export function useEyeTrackingTransitions(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentEyeTrackingTransitions(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
