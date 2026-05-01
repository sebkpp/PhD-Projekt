import ParticipantConfigBox from './components/ParticipantConfigurationBox.jsx'
import QuestionnaireQRCodeGroup from '../overview/components/QRCode/ParticipantStartQRCodeGroup.jsx'
import QuestionnaireSelector from '@/features/questionnaire/components/questionnaireSelector/QuestionnaireSelector.jsx';
import { useState } from 'react';

export default function ConfigurationForm({
                                              trialConfigs,
                                              activeIndex,
                                              setActiveIndex,
                                              validationErrors,
                                              handleChange,
                                              handleNext,
                                              status,
                                              bothConnected,
                                              MAX_TRIALS,
                                              setTrialConfigs,
                                              loading, experiment_id,
                                              selectedQuestionnaires, setSelectedQuestionnaires
                                          }) {

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
                        status={status}
                        setConfigs={handleChange}
                        disabled={!bothConnected}
                        validationErrors={validationErrors.filter(e => e.trialIndex === activeIndex)}
                    />
                </div>
            </div>

            <div className="my-6">
                <h2 className="text-xl font-semibold mb-2 text-white">Fragebögen für die Probanden</h2>
                <QuestionnaireSelector
                    selectedQuestionnaires={selectedQuestionnaires}
                    setSelectedQuestionnaires={setSelectedQuestionnaires}
                />
            </div>

            <div className="flex gap-8 items-center mt-4">
                <QuestionnaireQRCodeGroup experiment_id={experiment_id} status={status} />
            </div>

            {/* Weiter-Button */}
            <div className="mt-8">
                <button
                    onClick={handleNext}
                    disabled={!bothConnected || loading}
                    className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50"
                >
                    {loading ? "Speichere Trials..." : "➡️ Weiter zu „Warten auf Probanden“"}
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
