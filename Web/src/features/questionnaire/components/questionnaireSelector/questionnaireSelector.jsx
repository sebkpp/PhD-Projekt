import { useQuestionnaires } from './useQuestionnaires.js'
import { useState } from 'react'

export default function QuestionnaireSelector({ selectedQuestionnaires, onChange }) {
    const { allQuestionnaires, loading, error } = useQuestionnaires()
    const [filter, setFilter] = useState('')

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1)
    const PAGE_SIZE = 4

    // Gefilterte Fragebögen
    const filteredQuestionnaires = allQuestionnaires.filter(q =>
        q.name.toLowerCase().includes(filter.toLowerCase())
    )

    // Anzahl Seiten
    const totalPages = Math.ceil(filteredQuestionnaires.length / PAGE_SIZE)

    // Fragebögen der aktuellen Seite
    const pagedQuestionnaires = filteredQuestionnaires.slice(
        (currentPage - 1) * PAGE_SIZE,
        currentPage * PAGE_SIZE
    )

    // Handler für Klick auf Kachel (Selektieren/Deselektieren)
    const toggleSelect = (q) => {
        const isSelected = selectedQuestionnaires.some(s => s.questionnaire_id === q.questionnaire_id)
        if (isSelected) {
            onChange(selectedQuestionnaires.filter(s => s.questionnaire_id !== q.questionnaire_id))
        } else {
            onChange([...selectedQuestionnaires, q])
        }
    }

    // Pagination Controls
    const goPrev = () => setCurrentPage(Math.max(1, currentPage - 1))
    const goNext = () => setCurrentPage(Math.min(totalPages, currentPage + 1))

    return (
        <div className="flex gap-8">
            {/* Linke Seite: Verfügbare Fragebögen */}
            <div className="flex-1 border border-gray-600 p-4 rounded bg-gray-800 max-h-[400px] flex flex-col">
                <h2 className="font-bold mb-4 text-white">Verfügbare Fragebögen</h2>

                <input
                    type="text"
                    placeholder="Filter..."
                    className="w-full mb-4 p-2 rounded border border-gray-600 bg-gray-900 text-white"
                    value={filter}
                    onChange={e => {
                        setFilter(e.target.value)
                        setCurrentPage(1) // Zurück auf Seite 1 bei Filter-Änderung
                    }}
                />

                {loading ? (
                    <p className="text-gray-400">Lade...</p>
                ) : error ? (
                    <p className="text-red-400">Fehler beim Laden der Fragebögen</p>
                ) : (
                    <>
                        <div className="grid grid-cols-2 gap-4 overflow-auto flex-grow">
                            {pagedQuestionnaires.length === 0 && (
                                <p className="text-gray-400 col-span-2 text-center">Keine Fragebögen gefunden</p>
                            )}
                            {pagedQuestionnaires.map(q => {
                                const isSelected = selectedQuestionnaires.some(s => s.questionnaire_id === q.questionnaire_id)
                                return (
                                    <div
                                        key={q.questionnaire_id}
                                        onClick={() => toggleSelect(q)}
                                        className={`cursor-pointer p-3 rounded border text-white ${
                                            isSelected
                                                ? 'border-green-400 bg-green-900'
                                                : 'border-gray-600 hover:border-green-400 hover:bg-green-800'
                                        }`}
                                    >
                                        {q.name}
                                    </div>
                                )
                            })}
                        </div>

                        {/* Pagination Buttons */}
                        <div className="mt-4 flex justify-center gap-4">
                            <button
                                onClick={goPrev}
                                disabled={currentPage === 1}
                                className="px-3 py-1 rounded bg-gray-700 text-white disabled:opacity-50"
                            >
                                Zurück
                            </button>
                            <span className="text-white self-center">
                Seite {currentPage} von {totalPages}
              </span>
                            <button
                                onClick={goNext}
                                disabled={currentPage === totalPages}
                                className="px-3 py-1 rounded bg-gray-700 text-white disabled:opacity-50"
                            >
                                Weiter
                            </button>
                        </div>
                    </>
                )}
            </div>

            {/* Rechte Seite: Ausgewählte Fragebögen (bleibt unverändert) */}
            <div className="flex-1 border border-gray-600 p-4 rounded bg-gray-800 max-h-[400px] overflow-auto">
                <h2 className="font-bold mb-4 text-white">Ausgewählte Fragebögen (Reihenfolge)</h2>

                <ul className="space-y-2">
                    {selectedQuestionnaires.length === 0 && (
                        <li className="text-gray-400">Keine Fragebögen ausgewählt</li>
                    )}
                    {selectedQuestionnaires.map((q, i) => {
                        const full = allQuestionnaires.find(aq => aq.questionnaire_id === q.questionnaire_id);
                        const name = full ? full.name : '';
                        return (
                            <li
                                key={q.questionnaire_id+ '-' + i}
                                className="flex items-center justify-between p-2 border border-gray-700 rounded bg-gray-900 text-white"
                            >
                                <span>{name}</span>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => {
                                            if (i !== 0) {
                                                const newSelected = [...selectedQuestionnaires]
                                                ;[newSelected[i - 1], newSelected[i]] = [newSelected[i], newSelected[i - 1]]
                                                onChange(newSelected)
                                            }
                                        }}
                                        disabled={i === 0}
                                        className="disabled:opacity-50 px-2"
                                        title="Nach oben verschieben"
                                    >
                                        ↑
                                    </button>
                                    <button
                                        onClick={() => {
                                            if (i !== selectedQuestionnaires.length - 1) {
                                                const newSelected = [...selectedQuestionnaires]
                                                ;[newSelected[i + 1], newSelected[i]] = [newSelected[i], newSelected[i + 1]]
                                                onChange(newSelected)
                                            }
                                        }}
                                        disabled={i === selectedQuestionnaires.length - 1}
                                        className="disabled:opacity-50 px-2"
                                        title="Nach unten verschieben"
                                    >
                                        ↓
                                    </button>
                                    <button
                                        onClick={() => {
                                            onChange(selectedQuestionnaires.filter(s => s.questionnaire_id !== q.questionnaire_id))
                                        }}
                                        className="text-red-500 px-2"
                                        title="Entfernen"
                                    >
                                        ✕
                                    </button>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            </div>
        </div>
    )
}
