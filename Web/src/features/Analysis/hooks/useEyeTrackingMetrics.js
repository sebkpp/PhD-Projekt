import { useEffect, useState } from "react";
import { fetchExperimentEyeTracking } from "../services/eyeTrackingService";

export function useEyeTrackingMetrics(experimentId) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId) return;
        setLoading(true);
        setError(null);

        fetchExperimentEyeTracking(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId]);

    return { data, loading, error };
}
