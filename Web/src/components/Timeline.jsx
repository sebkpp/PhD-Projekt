import { usePhase } from './PhaseProvider.jsx'

export default function Timeline() {
    const { currentPhase } = usePhase()
    console.log('[Timeline] aktuelle Phase:', currentPhase)
    const phases = [
        'Konfiguration',
        'Warten auf Probanden',
        'Trial läuft',
        'Fragebogen',
        'Beendet'
    ]

    return (
        <div className="flex justify-between items-center mb-8">
            {phases.map((phase, index) => {
                const isActive = phase === currentPhase
                const isCompleted = phases.indexOf(currentPhase) > index

                return (
                    <div key={phase} className="flex items-center flex-1">
                        <div
                            className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold 
                ${isActive ? 'bg-accent text-white' : isCompleted ? 'bg-green-600 text-white' : 'bg-gray-600 text-white'}`}
                        >
                            {index + 1}
                        </div>
                        <div className="ml-2 text-sm whitespace-nowrap text-gray-300">
                            {phase}
                        </div>
                        {index < phases.length - 1 && (
                            <div className="flex-1 h-[2px] bg-gray-600 mx-2" />
                        )}
                    </div>
                )
            })}
        </div>
    )
}
