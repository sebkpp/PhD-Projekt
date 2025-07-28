import { createContext, useContext, useState } from 'react'

const PhaseContext = createContext()

export function PhaseProvider({ children }) {
    const [currentPhase, setCurrentPhase] = useState('Konfiguration') // default

    return (
        <PhaseContext.Provider value={{ currentPhase, setCurrentPhase }}>
            {children}
        </PhaseContext.Provider>
    )
}

export function usePhase() {
    return useContext(PhaseContext)
}
