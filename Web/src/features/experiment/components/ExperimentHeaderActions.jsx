import { useTranslation } from 'react-i18next';

export default function ExperimentHeaderActions({ onNewExperiment, onEvaluate, studyStatus }) {
    const { t } = useTranslation('study');
    return (
        <div className="flex gap-4">
            <button
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!studyStatus || studyStatus === "Beendet"}
                onClick={onNewExperiment}
            >
                {t('overview.newExperiment')}
            </button>
            <button
                className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg shadow-md"
                onClick={onEvaluate}
            >
                {t('actions.evaluate')}
            </button>
        </div>
    );
}
