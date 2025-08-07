import { useExperimentForm } from './useExperimentForm'

export default function ExperimentForm() {
    const {
        name, setName,
        description, setDescription,
        researcher, setResearcher,
        loading,
        error,
        handleSubmit
    } = useExperimentForm()

    return (
        <div className="max-w-md w-full border border-border rounded-xl p-6 space-y-4 bg-gray-900 shadow-lg">
            <h1 className="text-2xl font-bold text-center mb-4">Neues Experiment anlegen</h1>

            <div className="space-y-2">
                <label htmlFor="experiment-name" className="block text-sm">Titel des Experiments *</label>
                <input
                    id="experiment-name"
                    type="text"
                    className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="z.B. Vergleich visueller Stimuli"
                />

                <label htmlFor="researcher" className="block text-sm mt-3">Versuchsleiter:in (optional)</label>
                <input
                    id="researcher"
                    type="text"
                    className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                    value={researcher}
                    onChange={(e) => setResearcher(e.target.value)}
                    placeholder="z.B. Mustermann"
                />

                <label htmlFor="description" className="block text-sm mt-3">Beschreibung (optional)</label>
                <textarea
                    id="description"
                    rows={3}
                    className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Detaillierte Beschreibung, Zielsetzung usw."
                />
            </div>

            {error && <p className="text-sm text-red-400">{error}</p>}

            <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
                {loading ? "Experiment wird erstellt..." : "Experiment anlegen"}
            </button>
        </div>
    )
}
