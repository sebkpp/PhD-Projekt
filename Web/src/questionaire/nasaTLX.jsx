import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function NasaTLX() {
    const { userId } = useParams()
    const [params] = useSearchParams()
    const navigate = useNavigate()
    const trialId = parseInt(params.get('trial'))

    const [values, setValues] = useState({})
    const [validationError, setValidationError] = useState(false)
    const [submitting, setSubmitting] = useState(false)

    const dimensions = [
        {
            key: 'mental',
            name: 'Geistige Anforderung',
            description: 'Wie viel geistige Anstrengung war bei der Informationsaufnahme und -verarbeitung erforderlich?'
        },
        {
            key: 'physical',
            name: 'Körperliche Anforderungen',
            description: 'Wie viel körperliche Aktivität war erforderlich?'
        },
        {
            key: 'temporal',
            name: 'Zeitliche Anforderung',
            description: 'Wieviel Zeitdruck empfanden Sie hinsichtlich der Häufigkeit oder dem Takt?'
        },
        {
            key: 'performance',
            name: 'Leistung',
            description: 'Wie gut haben Sie die Aufgabe Ihrer Meinung nach erledigt?'
        },
        {
            key: 'effort',
            name: 'Anstrengung',
            description: 'Wie viel Mühe mussten Sie investieren, um das Ziel zu erreichen?'
        },
        {
            key: 'frustration',
            name: 'Frustration',
            description: 'Wie genervt, gestresst oder unsicher haben Sie sich gefühlt?'
        }
    ]

    const handleClick = (key, event) => {
        const { left, width } = event.target.getBoundingClientRect()
        const clickX = event.clientX - left
        const value = Math.round((clickX / width) * 100)
        setValues(prev => ({ ...prev, [key]: value }))
        setValidationError(false)
    }

    const handleSubmit = async () => {
        const allFilled = dimensions.every(d => values[d.key] !== undefined)
        if (!allFilled) {
            setValidationError(true)
            return
        }

        setSubmitting(true)

        const payload = {
            userId: parseInt(userId),
            trialId,
            responses: values
        }

        try {
            const res = await fetch('/api/submit-nasatlx', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (res.ok) {
                navigate('/proband-thankyou')
            } else {
                alert("Fehler beim Senden. Bitte erneut versuchen.")
            }
        } catch (error) {
            console.error("Fehler beim Absenden:", error)
            alert("Verbindung zum Server fehlgeschlagen.")
        } finally {
            setSubmitting(false)
        }
    }

    const handleReset = () => {
        setValues({})
        setValidationError(false)
    }

    return (
        <div className="min-h-screen bg-background text-foreground p-6">
            <div className="max-w-3xl mx-auto">
                <h1 className="text-2xl font-bold mb-6">
                    NASA-TLX – Proband {userId}, Trial {trialId}
                </h1>

                <div className="space-y-8">
                    {dimensions.map(dim => {
                        const isPerformance = dim.key === 'performance'
                        const labelStart = isPerformance ? 'Gut' : 'Niedrig'
                        const labelEnd = isPerformance ? 'Schlecht' : 'Hoch'

                        return (
                            <div key={dim.key}>
                                {/* Titel + Beschreibung */}
                                <div className="flex items-start justify-between mb-1 gap-4">
                                    <label className="font-semibold">{dim.name}</label>
                                    <p className="text-sm text-gray-400 text-right">{dim.description}</p>
                                </div>

                                {/* Skala */}
                                <div className="flex items-center gap-4">
                                    <div className="relative w-full h-6">
                                        {/* Hintergrund */}
                                        <div className="absolute top-0 left-0 w-full h-6 bg-gray-700 rounded pointer-events-none" />

                                        {/* Hilfslinien */}
                                        {[...Array(21)].map((_, i) => (
                                            <div
                                                key={i}
                                                className={`absolute top-0 h-6 ${
                                                    i === 10 ? 'w-[2px] bg-gray-300' : 'w-[1px] bg-gray-400 opacity-70'
                                                } pointer-events-none`}
                                                style={{
                                                    left: `${i * 5}%`,
                                                    transform: 'translateX(-0.5px)'
                                                }}
                                            />
                                        ))}

                                        {/* Marker */}
                                        {values[dim.key] !== undefined && (
                                            <div
                                                className="absolute top-0 h-6 w-[2px] bg-accent pointer-events-none"
                                                style={{
                                                    left: `${values[dim.key]}%`,
                                                    transform: 'translateX(-1px)'
                                                }}
                                            />
                                        )}

                                        {/* Klickfläche */}
                                        <div
                                            className="absolute top-0 left-0 w-full h-6 cursor-pointer"
                                            onClick={(e) => handleClick(dim.key, e)}
                                        />
                                    </div>
                                </div>

                                {/* Beschriftung */}
                                <div className="flex justify-between text-sm text-gray-400 mt-1">
                                    <span>{labelStart}</span>
                                    <span>{labelEnd}</span>
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Button-Zeile */}
                <div className="mt-10 flex gap-4 justify-end">
                    <button
                        onClick={handleReset}
                        className="px-6 py-3 bg-gray-600 text-white rounded hover:bg-gray-500 transition-all"
                    >
                        🔄 Zurücksetzen
                    </button>

                    <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50"
                    >
                        {submitting ? 'Wird gesendet...' : 'Fragebogen absenden'}
                    </button>
                </div>

                {validationError && (
                    <p className="text-sm text-red-400 mt-3">
                        ⚠️ Bitte füllen Sie alle Skalen aus, bevor Sie fortfahren.
                    </p>
                )}
            </div>
        </div>
    )
}
