import { useEffect, useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import ParticipantConfigBox from '../components/ParticipantConfigurationBox.jsx'
import { usePhase } from '../components/PhaseProvider.jsx'
import QuestionnaireQRCodeGroup from '../components/QuestionnaireQRCodeGroup.jsx'

const MAX_TRIALS = 10

export default function ConfigPage() {
    const { experimentId } = useParams();
    const { setCurrentPhase } = usePhase()
    const navigate = useNavigate()
    const { players } = useOutletContext()
    const [validationErrors, setValidationErrors] = useState([])

    const [trialConfigs, setTrialConfigs] = useState([
        {
            1: { stimuli: {}, selectedStimuli: {}, avatar: '' },
            2: { stimuli: {}, selectedStimuli: {}, avatar: '' }
        }
    ])
    const [activeIndex, setActiveIndex] = useState(0)

    const connectedPlayers = Object.keys(players).filter(id => players[id].connected)
    const bothConnected = connectedPlayers.length === 2
    const [status, setStatus] = useState({ 1: { submitted: false, participant_id: null }, 2: { submitted: false, participant_id: null } })
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Lokale Update-Funktion für einzelne Trial-Änderungen
    const handleChange = (participant_id, field, value) => {
        const updated = [...trialConfigs]
        updated[activeIndex] = {
            ...updated[activeIndex],
            [participant_id]: {
                ...updated[activeIndex][participant_id],
                [field]: value
            }
        }
        setTrialConfigs(updated)
    }

    const validateConfigs = () => {
        const errors = []
        if (!status[1]?.participant_id || !status[2]?.participant_id) {
            errors.push({
                field: 'questionnaire',
                message: 'Beide Probanden müssen den Fragebogen ausgefüllt haben.'
            })
        }

        trialConfigs.forEach((trial, trialIndex) => {
            for (const id of [1, 2]) {
                const participant = trial[id]
                const stimuli = participant?.stimuli || {}
                const selected = participant?.selectedStimuli || {}
                const avatar = participant?.avatar || ''

                if (!avatar) {
                    errors.push({
                        trialIndex,
                        participant_id: id,
                        field: 'avatar',
                        message: `Trial ${trialIndex + 1}, Proband ${id}: Es muss eine Avatarsichtbarkeit ausgewählt werden.`
                    })
                }

                const hasActiveStimulus = Object.values(stimuli).some(v => v === true)
                if (!hasActiveStimulus) {
                    errors.push({
                        trialIndex,
                        participant_id: id,
                        field: 'stimuli',
                        message: `Trial ${trialIndex + 1}, Proband ${id}: Es muss mindestens ein Stimulus-Typ aktiviert sein.`
                    })
                }

                for (const type of Object.keys(stimuli)) {
                    if (stimuli[type] && !selected[type]) {
                        errors.push({
                            trialIndex,
                            participant_id: id,
                            field: `stimuli.${type}`,
                            message: `Trial ${trialIndex + 1}, Proband ${id}: Für aktivierten Stimulus "${type.toUpperCase()}" fehlt die spezifische Auswahl.`
                        })
                    }
                }
            }
        })

        return errors
    }

    const handleNext = async () => {
        const errors = validateConfigs()
        if (errors.length > 0) {
            setValidationErrors(errors)
            return
        }
        setValidationErrors([])

        const payload = {
            experiment_id: experimentId,
            trials: trialConfigs.map((cfg, index) => ({
                trial_number: index + 1,
                participants: {
                    1: {
                        ...cfg[1],
                        participant_id: status[1]?.participant_id
                    },
                    2: {
                        ...cfg[2],
                        participant_id: status[2]?.participant_id
                    }
                }
            }))
        }

        try {
            const res = await fetch('/api/trials', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (res.ok) {
                setCurrentPhase('Warten auf Probanden')
                navigate('/experiment/${experimentId}/overview')
            } else {
                alert('Fehler beim Speichern der Trials')
            }
        } catch (e) {
            console.error(e)
            alert('Serverfehler')
        }
    }

    useEffect(() => {
        if (!experimentId) return;

        const interval = setInterval(async () => {
            try {
                const res1 = await fetch('/api/participants/status/1')
                const res2 = await fetch('/api/participants/status/2')

                if (res1.ok && res2.ok) {
                    const data1 = await res1.json()
                    const data2 = await res2.json()
                    const newStatus = { 1: data1, 2: data2 }
                    setStatus({ 1: data1, 2: data2 })
                }
            } catch (err) {
                console.error('Fehler beim Abrufen des Status:', err)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Versuchs-Konfiguration</h1>

            {!bothConnected && (
                <p className="text-red-400 mb-4">
                    ⚠️ Beide Probanden müssen verbunden sein, bevor konfiguriert werden kann.
                </p>
            )}

            {/* Tabs + Inhalt gruppieren */}
            <div className="border border-border rounded-xl">
                {/* Tabs */}
                <div className="flex gap-2 overflow-x-auto px-4 pt-4 -mb-px">
                    {trialConfigs.map((_, index) => (
                        <div key={index} className="relative">
                            <button
                                onClick={() => setActiveIndex(index)}
                                className={`px-4 py-2 rounded-t border border-b-0 whitespace-nowrap ${
                                    activeIndex === index
                                        ? 'bg-accent text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }`}
                            >
                                Trial {index + 1}
                            </button>

                            {trialConfigs.length > 1 && (
                                <button
                                    onClick={() => {
                                        const updated = trialConfigs.filter((_, i) => i !== index)
                                        setTrialConfigs(updated)
                                        if (activeIndex >= updated.length) {
                                            setActiveIndex(Math.max(0, updated.length - 1))
                                        }
                                    }}
                                    className="absolute -top-2 -right-2 bg-gray-700 text-white hover:bg-red-500 transition-colors rounded-full w-5 h-5 text-xs shadow"
                                    title="Trial löschen"
                                >
                                    ✕
                                </button>
                            )}
                        </div>
                    ))}

                    {trialConfigs.length < MAX_TRIALS && (
                        <button
                            onClick={() => {
                                setTrialConfigs([
                                    ...trialConfigs,
                                    {
                                        1: { stimuli: {}, selectedStimuli: {}, avatar: '' },
                                        2: { stimuli: {}, selectedStimuli: {}, avatar: '' }
                                    }
                                ])
                                setActiveIndex(trialConfigs.length)
                            }}
                            className="px-4 py-2 bg-gray-800 text-gray-400 rounded-t hover:bg-gray-700"
                        >
                            ➕
                        </button>
                    )}
                </div>

                {/* Aktiver Tab-Inhalt */}
                <div className="p-4 border-t border-border bg-gray-800 rounded-b-xl">
                    <ParticipantConfigBox
                        configs={trialConfigs[activeIndex]}
                        setConfigs={handleChange}
                        disabled={!bothConnected}
                        validationErrors={validationErrors.filter(e => e.trialIndex === activeIndex)}
                    />
                </div>
            </div>

            <div className="flex gap-8 items-center">
                <QuestionnaireQRCodeGroup experimentId={experimentId} status={status} />
            </div>

            {/* Weiter-Button */}
            <div className="mt-8">
                <button
                    onClick={handleNext}
                    disabled={!bothConnected}
                    className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50"
                >
                    ➡️ Weiter zu „Warten auf Probanden“
                </button>
                {validationErrors.length > 0 && (
                    <div className="mt-4 bg-red-950 border border-red-700 p-4 rounded text-sm text-red-300 space-y-1">
                        <strong className="block text-red-400 mb-2">Bitte beheben Sie folgende Fehler:</strong>
                        {validationErrors.map((err, idx) => (
                            <div key={idx}>• {err.message}</div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
