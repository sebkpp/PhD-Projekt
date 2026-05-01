export default function ParticipantConfigCard({ id, config, status, disabled, validationErrors, stimulusOptions, avatarOptions, setConfigs }) {
    const hasError = (field) =>
        validationErrors?.some(e => e.participant_id === id && e.field === field)

    const handleStimuliChange = (type, checked) => {
        setConfigs(id, 'stimuli', { ...config.stimuli, [type]: checked })
    }

    const handleSelectedStimuliChange = (type, value) => {
        setConfigs(id, 'selectedStimuli', { ...config.selectedStimuli, [type]: value })
    }

    const handleAvatarChange = (value) => {
        setConfigs(id, 'avatar', value)
    }

    return (
        <div className="rounded-2xl border border-border bg-gray-800 p-6 shadow-md hover:shadow-lg transition-all">
            <h3 className="text-lg font-semibold text-foreground mb-4 border-b border-border pb-1">
                Proband {id}
                {status?.participant_id && (
                    <span className="text-gray-400 text-sm ml-2">(ID: {status.participant_id})</span>
                )}
            </h3>

            {/* Stimuli aktiv */}
            <div className="mb-2 text-sm">
                <label className="block font-medium mb-1">Aktive Stimuli:</label>
                <div className={`flex gap-4 border rounded px-2 py-1 ${
                    hasError('stimuli') ? 'border-red-500 bg-red-950' : 'border-transparent'
                }`}>
                    {['vis', 'aud', 'tak'].map(type => (
                        <label key={type} className="flex items-center gap-1">
                            <input
                                type="checkbox"
                                disabled={disabled}
                                checked={config?.stimuli?.[type] || false}
                                onChange={e => handleStimuliChange(type, e.target.checked)}
                            />
                            <span>{type.toUpperCase()}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Avatarsichtbarkeit */}
            <div className="mb-2 text-sm">
                <label className="block font-medium mb-1">Avatarsichtbarkeit:</label>
                <select
                    disabled={disabled}
                    className={`bg-gray-700 border rounded px-2 py-1 w-full ${
                        hasError('avatar') ? 'border-red-500' : 'border-border'
                    }`}
                    value={config.avatar || ''}
                    onChange={e => handleAvatarChange(e.target.value)}
                >
                    <option value="">Bitte wählen</option>
                    {avatarOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
            </div>

            {/* Auswahl der Stimuli pro Typ */}
            {['vis', 'aud', 'tak'].map(type =>
                    config.stimuli?.[type] && (
                        <div key={type} className="mb-2 text-sm">
                            <label className="block font-medium mb-1">
                                {type === 'vis' && 'Visueller Stimulus'}
                                {type === 'aud' && 'Auditiver Stimulus'}
                                {type === 'tak' && 'Taktiler Stimulus'}
                            </label>
                            <select
                                disabled={disabled}
                                className={`bg-gray-700 border rounded px-2 py-1 w-full ${
                                    hasError(`stimuli.${type}`) ? 'border-red-500' : 'border-border'
                                }`}
                                value={config.selectedStimuli?.[type] || ''}
                                onChange={e => handleSelectedStimuliChange(type, e.target.value)}
                            >
                                <option value="">Bitte wählen</option>
                                {stimulusOptions[type].map(option => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )
            )}
        </div>
    )
}
