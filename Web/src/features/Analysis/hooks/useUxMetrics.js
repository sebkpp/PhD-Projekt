import { useState, useEffect } from "react";
import { fetchUxMetrics } from "../services/uxMetricsService";

export function useUxMetrics(experimentId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!experimentId) return;
    setLoading(true);
    setError(null);

    fetchUxMetrics(experimentId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [experimentId]);

  return { data, loading, error };
}