import { useState, useEffect } from "react";
import { fetchStudies, deleteStudy } from "../services/studyService";

export function useStudies() {
    const [studies, setStudies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadStudies();
    }, []);

    async function loadStudies() {
        try {
            setLoading(true);
            const data = await fetchStudies();
            const sortedData = data.sort((a, b) => new Date(b.study_id) - new Date(a.study_id));
            setStudies(sortedData);
            setError(null); // Fehler zurücksetzen, falls erfolgreich
        } catch(err) {
            handleError(err, "Fehler beim Laden der Studien");
        } finally {
            setLoading(false);
        }
    }

    async function removeStudy(studyId) {
        try {
            await deleteStudy(studyId);
            setStudies(prev => prev.filter(s => s.study_id !== studyId));
            setError(null); // Fehler zurücksetzen, falls erfolgreich
        } catch (err) {
            handleError(err, "Fehler beim Löschen der Studie");
        }
    }

    function handleError(err, defaultMessage) {
        if (err.response && err.response.data && err.response.data.message) {
            setError(err.response.data.message); // API-spezifische Fehlermeldung
        } else {
            setError(defaultMessage); // Standardfehlermeldung
        }
    }

    return { studies, loading, error, removeStudy, reload: loadStudies };
}