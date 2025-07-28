export default function ParticipantConfigBox({ configs, setConfigs, disabled }) {
    const handleChange = (id, field, value) => {
        if (disabled) return; // Verhindert Änderungen, wenn deaktiviert
        setConfigs(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                [field]: value
            }
        }));
    };

    const stimulusOptions = {
        vis: [
            { value: 'vis_inner', label: 'Visuell – Inner Hand' },
            { value: 'vis_color', label: 'Visuell – Finger Color' }
        ],
        aud: [
            { value: 'aud_high', label: 'Auditiv – Hoch' },
            { value: 'aud_pulse', label: 'Auditiv – Puls' }
        ],
        tak: [
            { value: 'tak_vibe', label: 'Taktil – Vibration' },
            { value: 'tak_pulse', label: 'Taktil – Pulsfrequenz' }
        ]
    };

    return (
        <div className={`border border-border rounded-xl p-6 ${disabled ? 'opacity-50' : ''}`}>
            <h2 className="text-xl font-semibold mb-4">Probanden-Konfiguration</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[1, 2].map(id => {
                    const config = configs[id] || {};
                    return (
                        <div key={id} className="border border-border rounded-lg p-4 bg-background">
                            <h3 className="text-accent font-semibold mb-2">Proband {id}</h3>
                            {/* Stimuli aktiv */}
                            <div className="mb-2 text-sm">
                                <label className="block font-medium mb-1">Aktive Stimuli:</label>
                                <div className="flex gap-4">
                                    {['vis', 'aud', 'tak'].map(type => (
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
                                    className="bg-gray-700 border border-border rounded px-2 py-1 w-full"
                                    value={config.avatar || ''}
                                    onChange={(e) => handleChange(id, 'avatar', e.target.value)}
                                >
                                    <option value="">Bitte wählen</option>
                                    <option value="hands">Nur Hände</option>
                                    <option value="head">Hände + Kopf</option>
                                    <option value="full">Ganze Figur</option>
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
                                                className="bg-gray-700 border border-border rounded px-2 py-1 w-full"
                                                value={config.selectedStimuli?.[type] || ''}
                                                onChange={(e) =>
                                                    handleChange(id, 'selectedStimuli', {
                                                        ...config.selectedStimuli,
                                                        [type]: e.target.value
                                                    })
                                                }
                                            >
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
