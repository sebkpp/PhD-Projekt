import { useEffect, useState } from 'react'

export default function ParticipantConfigBox({ configs, setConfigs, disabled, validationErrors }) {
    const [stimulusOptions, setStimulusOptions] = useState({ vis: [], aud: [], tak: [] });
    const [avatarOptions, setAvatarOptions] = useState([]);

    const handleChange = (id, field, value) => {
        if (disabled) return
        setConfigs(id, field, value)
    }

    const hasError = (id, field) =>
        validationErrors?.some(
            (e) => e.probandId === id && e.field === field
        )

    useEffect(() => {
        fetch('/api/stimuli')
            .then(res => res.json())
            .then(data => {
                const grouped = { vis: [], aud: [], tak: [] }

                const typeMap = {
                    visual: 'vis',
                    auditory: 'aud',
                    tactile: 'tak'
                }

                data.forEach(s => {
                    const typeKey = typeMap[s.type]
                    if (typeKey) {
                        grouped[typeKey].push({ value: s.id, label: s.name })
                    }
                })

                setStimulusOptions(grouped)
            })

        fetch('/api/avatar-visibility')
            .then(res => res.json())
            .then(data => {
                setAvatarOptions(data.map(opt => ({ value: opt.id, label: opt.label })))
            })
    }, []);

    return (
        <div className={`${disabled ? 'opacity-50' : ''}`}>
            <h2 className="text-xl font-semibold mb-4">Probanden-Konfiguration</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map(id => {
                    const config = configs[id] || {};
                    return (
                        <div key={id} className="rounded-2xl border border-border bg-gray-800 p-6 shadow-md hover:shadow-lg transition-all">
                            <h3 className="text-lg font-semibold text-foreground mb-4 border-b border-border pb-1">Proband {id}</h3>
                            {/* Stimuli aktiv */}
                            <div className="mb-2 text-sm">
                                <label className="block font-medium mb-1">Aktive Stimuli:</label>
                                <div
                                    className={`flex gap-4 border rounded px-2 py-1 ${
                                        hasError(id, 'stimuli') ? 'border-red-500 bg-red-950' : 'border-transparent'
                                    }`}>                                    {['vis', 'aud', 'tak'].map(type => (
                                        <label key={type} className="flex items-center gap-1">
                                            <input
                                                type="checkbox"
                                                disabled={disabled}
                                                checked={config?.stimuli?.[type] || false}
                                                onChange={(e) =>
                                                    handleChange(id, 'stimuli', {
                                                        ...config.stimuli,
                                                        [type]: e.target.checked
                                                    })
                                                }
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
                                        hasError(id, 'avatar') ? 'border-red-500' : 'border-border'
                                    }`}
                                    value={config.avatar || ''}
                                    onChange={(e) => handleChange(id, 'avatar', e.target.value)}
                                >
                                    <option value="">Bitte wählen</option>
                                    {avatarOptions.map(opt => (
                                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                                    ))}
                                </select>
                            </div>
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
                                                    hasError(id, `stimuli.${type}`) ? 'border-red-500' : 'border-border'
                                                }`}
                                                value={config.selectedStimuli?.[type] || ''}
                                                onChange={(e) =>
                                                    handleChange(id, 'selectedStimuli', {
                                                        ...config.selectedStimuli,
                                                        [type]: e.target.value
                                                    })
                                                }>
                                                <option value="">Bitte wählen</option>
                                                {stimulusOptions[type].map((option) => (
                                                    <option key={option.value} value={option.value}>
                                                        {option.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    )
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
