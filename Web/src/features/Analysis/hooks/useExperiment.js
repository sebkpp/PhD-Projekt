import { useEffect, useState } from "react";
import { fetchExperimentById } from "../services/experimentService";

export function useExperiment(experimentId) {
    const [experiment, setExperiment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId) return;
        setLoading(true);
        setError(null);
        fetchExperimentById(experimentId)
            .then(data => setExperiment(data))
            .catch(err => setError(err))
            .finally(() => setLoading(false));
    }, [experimentId]);

    return { experiment, loading, error };
}