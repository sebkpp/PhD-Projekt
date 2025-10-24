import { useEffect, useState } from "react";
import { fetchStimuliOptions } from "../services/stimuliOptionService";

export function useStimuliOptions() {
    const [options, setOptions] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        fetchStimuliOptions()
            .then(data => {
                setOptions(data);
                setError(null);
            })
            .catch(err => setError(err))
            .finally(() => setLoading(false));
    }, []);

    return { filtered_stimuli_options: options, loading, error };
}