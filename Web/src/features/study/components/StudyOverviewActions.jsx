import { useTranslation } from 'react-i18next'

export default function StudyOverviewActions({ onNewStudy, onStatistics }) {
    const { t } = useTranslation('study')
    return (
        <div className="flex gap-2">
            <button
                onClick={onNewStudy}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
            >
                {t('overview.newStudy')}
            </button>
            <button
                onClick={onStatistics}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
            >
                {t('actions.evaluate')}
            </button>
        </div>
    );
}