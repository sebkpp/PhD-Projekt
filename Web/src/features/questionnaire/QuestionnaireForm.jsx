import {useEffect, useMemo, useState} from 'react'
import DynamicQuestionnaireForm from './components/dynamic/DynamicQuestionnaireForm.jsx'
import { useSubmitQuestionnaire } from '@/features/questionnaire/hooks/useSubmitQuestionnaire'

export default function QuestionnaireForm({
                                              questionnaire,
                                              onNext,
                                              participantId,
                                              trialId,
                                              resetSignal
}) {
    const initialValues = useMemo(() => ({}), [])
    const [isValid, setIsValid] = useState(false);

    const {
        values: responses,
        error,
        validationErrors,
        loading,
        handleChange,
        handleSubmit,
        reset
    } = useSubmitQuestionnaire({
        initialValues,
        trialId,
        questionnaireName: questionnaire?.name,
        participantId,
        onSubmitSuccess: onNext
    });

    async function onSubmit(e) {
        e.preventDefault()

        const questionKeys = questionnaire?.items?.map(i => i.item_name) ?? []

        if (!responses || Object.keys(responses).length === 0) {
            alert('Bitte füllen Sie den Fragebogen aus.');
            return;
        }

        const missing = questionKeys.filter(key => {
            const val = responses[key];
            return val === undefined ||
                val === null ||
                val === '' ||
                (Array.isArray(val) && val.length === 0) ||
                (typeof val === 'number' && isNaN(val));
        });

        if (missing.length > 0) {
            alert('Bitte alle Fragen beantworten: ' + missing.join(', '));
            return;
        }

        try {
            const success = await handleSubmit();
            if (success) {
                onNext();
            }
        } catch (error) {
            console.error('Fehler beim Absenden:', error);
        }
    }

    useEffect(() => {
        reset()
    }, [resetSignal, reset])

    return (
        <form onSubmit={onSubmit} className="space-y-6 bg-background text-foreground p-6 rounded-md max-w-3xl mx-auto">
            <DynamicQuestionnaireForm
                questionnaire={questionnaire}
                onChange={handleChange}
                responses={responses}
                submitting={loading}
                error={error}
                participantId={participantId}
                trialId={trialId}
                onValidationChange={setIsValid}
            />

            {error && <p className="text-red-500">{error}</p>}

            {validationErrors && Object.keys(validationErrors).length > 0 && (
                <div className="text-red-600">
                    <p>Bitte füllen Sie alle Felder aus:</p>
                    <ul>
                        {Object.entries(validationErrors).map(([field, msg]) => (
                            <li key={field}>{field}: {msg}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="flex gap-4 justify-end mt-4">
                <button
                    type="button"
                    onClick={reset}
                    disabled={loading}
                    className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-500 transition"
                >
                    Zurücksetzen
                </button>

                <button
                    type="submit"
                    disabled={loading || !isValid}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition"
                >
                    {loading ? 'Senden...' : 'Weiter'}
                </button>
            </div>
        </form>
    )
}
