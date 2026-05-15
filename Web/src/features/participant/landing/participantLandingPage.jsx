import { useLandingState } from './useLandingState'
import { useTranslation } from 'react-i18next'

export default function ParticipantLanding() {
    const { t } = useTranslation('participant')

    const {
        experimentId,
        slot,
        handleStartDemography,
    } = useLandingState()


    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4 text-center relative">
            {/* Info oben rechts */}
            <div className="absolute top-4 right-4 text-sm text-gray-500">
                {t('landing.experiment')}: <span className="font-mono text-gray-300">{experimentId}</span><br />
                {t('landing.slot')}: <span className="font-mono text-gray-300">{slot}</span>
            </div>

            <h1 className="text-2xl font-bold mb-4">{t('landing.welcome')}</h1>

            <>
                <p className="text-lg text-gray-400 max-w-md mb-6">
                    {t('landing.demographyPrompt')}
                </p>
                <button
                    onClick={handleStartDemography}
                    className="px-6 py-3 bg-accent text-white rounded hover:bg-accent/80 transition"
                >
                    {t('landing.startQuestionnaire')}
                </button>
            </>
        </div>
    )
}
