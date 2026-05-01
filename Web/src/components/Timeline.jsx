import { usePhase } from './PhaseProvider.jsx'
import React from 'react'

export default function Timeline() {
    const { currentPhase, totalTrials, completedTrials } = usePhase()
    const phases = ['Vorbereitung', 'Versuch', 'Fragebogen', 'Beendet']
    const remaining = Math.max(totalTrials - completedTrials, 0)

    return (
        <div className="w-full mb-12">
            <div className="flex justify-between relative">
                {phases.map((phase, index) => {
                    const isActive = phase === currentPhase
                    const isCompleted = phases.indexOf(currentPhase) > index

                    return (
                        <div key={phase} className="flex-1 flex flex-col items-center relative">
                            {/* Linien */}
                            {index > 0 && (
                                <div
                                    className={`absolute left-0 w-1/2 h-[2px] top-[20px]
            ${isCompleted ? 'bg-green-600' : 'bg-gray-600'}`}
                                />
                            )}
                            {index < phases.length - 1 && (
                                <div
                                    className={`absolute right-0 w-1/2 h-[2px] top-[20px]
            ${isCompleted ? 'bg-green-600' : 'bg-gray-600'}`}
                                />
                            )}

                            {/* Kreis */}
                            <div
                                className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold z-10
                                    ${
                                    isActive
                                        ? 'bg-accent text-white'
                                        : isCompleted
                                            ? 'bg-green-600 text-white'
                                            : 'bg-gray-600 text-white'
                                }`}
                            >
                                {index + 1}
                            </div>

                            {/* Label */}
                            <div className="mt-2 text-center text-sm text-gray-300">
                                {phase}
                            </div>

                            {/* Wiederholungsanzeige */}
                            {index === 1 && remaining > 0 && (
                                <div className="absolute top-1/2 left-full transform -translate-x-1/2 -translate-y-1/2 text-xs text-gray-400 flex items-center gap-1">
                                    <span className="text-lg">↺</span>
                                    <span>{remaining}×</span>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
