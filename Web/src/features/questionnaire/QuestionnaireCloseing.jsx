import { useTranslation } from 'react-i18next'

export default function QuestionnaireClosing() {
    const { t } = useTranslation('questionnaire')
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 px-4">
            <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-md max-w-md text-center">
                <h1 className="text-3xl font-semibold text-gray-800 dark:text-white mb-4">
                    {t('closing.title')}
                </h1>
                <p className="text-gray-600 dark:text-gray-300 text-lg mb-6">
                    {t('closing.saved')}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                    {t('closing.instructions')}
                </p>
            </div>
        </div>
    );
}
