import { useState, useCallback } from 'react';
import { submitQuestionnaire } from '../service/questionnaireService';

function validate(values, requiredFields) {
    const errors = {};

    if (!values || Object.keys(values).length === 0) {
        errors._form = 'Keine Antworten vorhanden';
        return errors;
    }

    requiredFields.forEach(key => {
        const value = values[key];
        if (value === undefined ||
            value === null ||
            value === '' ||
            (Array.isArray(value) && value.length === 0) ||
            (typeof value === 'number' && isNaN(value))) {
            errors[key] = 'Bitte ausfüllen';
        }
    });

    return errors;
}

export function useSubmitQuestionnaire({
                                           initialValues = {},
                                           requiredFields = [],
                                           trialId,
                                           questionnaireName,
                                           participantId,
                                           onSubmitSuccess
                                       } = {}) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [values, setValues] = useState(initialValues);
    const [validationErrors, setValidationErrors] = useState({});

    const reset = useCallback(() => {
        setValues(initialValues);
        setError(null);
        setValidationErrors({});
    }, [initialValues]);

    function handleChange(questionId, value) {
        setValues(prev => ({ ...prev, [questionId]: value }));
    }

    const handleSubmit = useCallback(async () => {
        const errors = validate(values, requiredFields);
        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            return false;  // Indikator für Fehler
        }

        setLoading(true);
        setError(null);
        try {
            await submitQuestionnaire(participantId, trialId, questionnaireName, values);
            setValidationErrors({});
            if (onSubmitSuccess) onSubmitSuccess();
            return true;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [values, requiredFields, onSubmitSuccess]);

    return { values, setValues, error, validationErrors, loading, handleChange, handleSubmit, reset };
}
