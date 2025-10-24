import {createContext, useCallback, useContext, useState} from 'react'

const PhaseContext = createContext()

export function PhaseProvider({ children }) {
    const phaseOrder = ['Vorbereitung', 'Versuch', 'Fragebogen', 'Beendet']
    const [currentPhase, setCurrentPhase] = useState(phaseOrder[0]) // default
    const [totalTrials, setTotalTrials] = useState(0)
    const [completedTrials, setCompletedTrials] = useState(0)
    const [timeline, setTimeline] = useState([phaseOrder[0]])

    const nextPhase = useCallback(() => {
        const currentIdx = phaseOrder.indexOf(currentPhase)
        if (currentIdx < phaseOrder.length - 1) {
            const next = phaseOrder[currentIdx + 1]
            setCurrentPhase(next)
            setTimeline(prev => [...prev, next])
        }
    }, [currentPhase])

    return (
        <PhaseContext.Provider value={{
            currentPhase,
            setCurrentPhase,
            totalTrials,
            setTotalTrials,
            completedTrials,
            setCompletedTrials,
            timeline,
            nextPhase
        }}>
            {children}
        </PhaseContext.Provider>
    )
}

export function usePhase() {
    return useContext(PhaseContext)
}
