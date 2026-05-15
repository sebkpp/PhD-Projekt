import ParticipantConfigCard from './ParticipantConfigCard'
import { useStimulusOptions } from './useStimuliOptions'
import { useAvatarOptions } from './useAvatarOptions'
import { useTranslation } from 'react-i18next'

export default function ParticipantConfigBox({ configs, status, setConfigs, disabled, validationErrors }) {
    const { t } = useTranslation('configuration')
    const { stimulusOptions, error: stimulusError } = useStimulusOptions()
    const { avatarOptions, error: avatarError } = useAvatarOptions()

    if (stimulusError || avatarError) {
        return (
            <div className="p-4 text-red-500">
                {t('participantBox.loadError')}
            </div>
        )
    }

    return (
        <div className={`${disabled ? 'opacity-50' : ''}`}>
            <h2 className="text-xl font-semibold mb-4">{t('participantBox.title')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map(id => (
                    <ParticipantConfigCard
                        key={id}
                        id={id}
                        config={configs[id] || {}}
                        status={status?.[id]}
                        disabled={disabled}
                        validationErrors={validationErrors}
                        stimulusOptions={stimulusOptions}
                        avatarOptions={avatarOptions}
                        setConfigs={setConfigs}
                    />
                ))}
            </div>
        </div>
    )
}
