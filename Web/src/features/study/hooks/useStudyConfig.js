import {useEffect, useState} from "react";
import {createStudy, fetchStudyById, updateStudy} from "../services/studyService";

export function useStudyConfig(studyId) {
    const [config, setConfig] = useState();
    const [localConfig, setLocalConfig] = useState();
    const [error, setError] = useState(null);
    const [currentId, setCurrentId] = useState(studyId);

    useEffect(() => {
        if (studyId) loadConfig();
    }, [studyId]);

    useEffect(() => {
        setLocalConfig(config);
    }, [config]);

    async function loadConfig() {
        try {
            const data = await fetchStudyById(studyId);
            setConfig(data);
            setError(null);
        } catch (err) {
            setError(err.message || "Fehler beim Laden der Studienkonfiguration");
        }
    }

    function updateLocalConfig(field, value) {
        setLocalConfig(prev => ({ ...prev, [field]: value }));
    }

    async function saveConfig(status) {
        if (!localConfig.config?.name?.trim()) return;

        try {
            const payload = {
                ...localConfig,
                status
            };

            console.log("Saving config:", payload);
            let result;
            if (currentId) {
                result = await updateStudy(currentId, payload);
            } else {
                result = await createStudy(payload);
                setCurrentId(result.id);
            }
            setConfig(result);
            setError(null);
        } catch (err) {
            setError("Fehler beim Speichern");
        }
    }

    return { localConfig, error, updateLocalConfig, saveConfig, studyId: currentId };
}