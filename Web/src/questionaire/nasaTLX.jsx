import { useState } from 'react'

const dimensions = [
    {
        name: 'Geistige Anforderung',
        description: 'Wie viel geistige Anstrengung war bei der Informationsaufnahme und verarbeitung erforderlich?'
    },
    {
        name: 'Körperliche Anforderungen',
        description: 'Wie viel körperliche Aktiviät war erforderlich?'
    },
    {
        name: 'Zeitliche Anforderung',
        description: 'Wieviel Zeitdruck empfanden Sie hinsichtlich der Häufigkeit oder dem Takt?'
    },
    {
        name: 'Leistung',
        description: 'Wie gut haben Sie die Aufgabe Ihrer Meinung nach erledigt?'
    },
    {
        name: 'Anstrengung',
        description: 'Wie viel Mühe mussten Sie investieren, um das Ziel zu erreichen?'
    },
    {
        name: 'Frustration',
        description: 'Wie genervt, gestresst oder unsicher haben Sie sich gefühlt?'
    }
]

export default function NasaTLX() {
    const [values, setValues] = useState({})
    const [validationError, setValidationError] = useState(false)

    const handleClick = (dim, event) => {
        const { left, width } = event.target.getBoundingClientRect()
        const clickX = event.clientX - left
        const value = Math.round((clickX / width) * 100)
        setValues(prev => ({ ...prev, [dim]: value }))
        setValidationError(false) // Fehler zurücksetzen
    }

    const handleSubmit = () => {
        const allFilled = dimensions.every(d => values[d.name] !== undefined)
        if (!allFilled) {
            setValidationError(true)
            return
        }

        console.log('NASA-TLX Werte:', values)
        // TODO: POST an Flask senden
        setValidationError(false)
    }

    const handleReset = () => {
        setValues({})
        setValidationError(false)
    }

    return (
        <div className="min-h-screen bg-background text-foreground p-6">
            <h1 className="text-2xl font-bold mb-6">NASA-TLX Fragebogen</h1>

            <div className="space-y-8 max-w-3xl">
                {dimensions.map(dim => {
                    const isPerformance = dim.name.includes('Leistung')
                    const labelStart = isPerformance ? 'Gut' : 'Niedrig'
                    const labelEnd = isPerformance ? 'Schlecht' : 'Hoch'

                    return (
                        <div key={dim.name}>
                            {/* Titel + Beschreibung */}
                            <div className="flex items-start justify-between mb-1 gap-4">
                                <label className="font-semibold">{dim.name}</label>
                                <p className="text-sm text-gray-400 text-right">{dim.description}</p>
                            </div>

                            {/* Skala mit Hilfslinien & Marker */}
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
                                    {values[dim.name] !== undefined && (
                                        <div
                                            className="absolute top-0 h-6 w-[2px] bg-accent pointer-events-none"
                                            style={{
                                                left: `${values[dim.name]}%`,
                                                transform: 'translateX(-1px)'
                                            }}
                                        />
                                    )}

                                    {/* Klick-Overlay */}
                                    <div
                                        className="absolute top-0 left-0 w-full h-6 cursor-pointer"
                                        onClick={(e) => handleClick(dim.name, e)}
                                    />
                                </div>
                            </div>

                            {/* Endbeschriftung */}
                            <div className="flex justify-between text-sm text-gray-400 mt-1">
                                <span>{labelStart}</span>
                                <span>{labelEnd}</span>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Buttons */}
            <div className="mt-10 flex flex-col gap-2">
                <div className="flex gap-4">
                    <button
                        onClick={handleSubmit}
                        className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition-all">
                        📨 Absenden
                    </button>

                    <button
                        onClick={handleReset}
                        className="px-6 py-3 bg-gray-600 text-white rounded hover:bg-gray-500 transition-all">
                        🔄 Zurücksetzen
                    </button>
                </div>

                {validationError && (
                    <p className="text-sm text-red-400 mt-1">
                        ⚠️ Bitte füllen Sie alle Skalen aus, bevor Sie fortfahren.
                    </p>
                )}
            </div>
        </div>
    )
}