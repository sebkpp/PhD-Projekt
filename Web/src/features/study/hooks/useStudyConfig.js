import {useEffect, useState} from "react";
import {createStudy, fetchStudyById, updateStudy} from "../services/studyService";
import i18n from '@/i18n';

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
            setError(err.message || i18n.t('study:errors.loadConfig'));
        }
    }

    function updateLocalConfig(field, value) {
        setLocalConfig(prev => ({ ...prev, [field]: value }));
    }

    async function saveConfig(status) {
        if (!localConfig?.config?.name?.trim()) {
            setError(i18n.t('study:errors.nameRequired'));
            return false;
        }

        try {
            const payload = {
                ...localConfig,
                status
            };

            let result;
            if (currentId) {
                result = await updateStudy(currentId, payload);
            } else {
                result = await createStudy(payload);
                setCurrentId(result.study_id);
            }
            setConfig(result);
            setError(null);
            return true;
        } catch (err) {
            setError(i18n.t('study:errors.saveFailed', { msg: err.message ?? i18n.t('common:status.unknown') }));
            return false;
        }
    }

    return { localConfig, error, updateLocalConfig, saveConfig, studyId: currentId };
}