import { useState, useEffect } from "react";
import { fetchStudies, deleteStudy } from "../services/studyService";
import i18n from '@/i18n';

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
            handleError(err, i18n.t('study:errors.loadStudies'));
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
            handleError(err, i18n.t('study:errors.deleteStudy'));
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