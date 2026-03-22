import { useState, useEffect } from "react";
import { fetchExperimentSaccadeRate } from "@/features/Analysis/services/eyeTrackingService.js";

export function useSaccadeRate(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentSaccadeRate(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
