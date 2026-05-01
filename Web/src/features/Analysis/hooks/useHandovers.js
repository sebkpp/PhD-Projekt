import { useEffect, useState } from "react";
import { fetchHandoversByExperimentId } from "@/features/Analysis/services/experimentService";

export function useHandovers(experimentId) {
    const [handovers, setHandovers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId) return;
        setLoading(true);
        setError(null);
        fetchHandoversByExperimentId(experimentId)
            .then(setHandovers)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId]);

    return { handovers, loading, error };
}