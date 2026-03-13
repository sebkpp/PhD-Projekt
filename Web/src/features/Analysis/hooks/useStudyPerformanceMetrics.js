import { useEffect, useState } from "react";
import { fetchStudyPerformance } from "../services/studyAnalysisService";

export function useStudyPerformanceMetrics(studyId) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId) return;
        setLoading(true);
        setError(null);

        fetchStudyPerformance(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId]);

    return { data, loading, error };
}
