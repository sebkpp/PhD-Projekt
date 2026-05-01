import { useEffect, useState } from "react";
import { fetchStudyPerformance } from "../services/studyAnalysisService";

export function useStudyPerformanceMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchStudyPerformance(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId, enabled]);

    return { data, loading, error };
}
