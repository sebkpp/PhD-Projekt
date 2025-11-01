import { useEffect, useState } from "react";
import { fetchPerformanceMetrics } from "../services/performanceMetrics";

export function usePerformanceMetrics(experimentId) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId) return;
        setLoading(true);
        setError(null);

        fetchPerformanceMetrics(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId]);
    return { data, loading, error };
}