import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function NewExperimentPage() {
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [researcher, setResearcher] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    const handleCreate = async () => {
        if (!name.trim()) {
            setError('Bitte gib einen Namen für das Experiment ein.')
            return
        }

        setLoading(true)
        setError(null)

        try {
            const res = await fetch('/api/experiments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    description,
                    researcher
                })
            })

            if (res.ok) {
                const data = await res.json()
                const experimentId = data.experimentId
                navigate(`/experiment/${experimentId}/configure`)
            } else {
                setError('Fehler beim Anlegen des Experiments.')
            }
        } catch (e) {
            console.error(e)
            setError('Verbindungsfehler zum Server.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground p-6">
            <div className="max-w-md w-full border border-border rounded-xl p-6 space-y-4 bg-gray-900 shadow-lg">
                <h1 className="text-2xl font-bold text-center mb-4">Neues Experiment anlegen</h1>

                <div className="space-y-2">
                    <label className="block text-sm">Titel des Experiments *</label>
                    <input
                        type="text"
                        className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="z. B. Vergleich visueller Stimuli"
                    />

                    <label className="block text-sm mt-3">Versuchsleiter:in (optional)</label>
                    <input
                        type="text"
                        className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        value={researcher}
                        onChange={(e) => setResearcher(e.target.value)}
                        placeholder="z. B. Mustermann"
                    />

                    <label className="block text-sm mt-3">Beschreibung (optional)</label>
                    <textarea
                        rows={3}
                        className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Detaillierte Beschreibung, Zielsetzung usw."
                    />
                </div>

                {error && <p className="text-sm text-red-400">{error}</p>}

                <button
                    onClick={handleCreate}
                    disabled={loading}
                    className="w-full px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50"
                >
                    {loading ? "Experiment wird erstellt..." : "Experiment anlegen"}
                </button>
            </div>
        </div>
    )
}
