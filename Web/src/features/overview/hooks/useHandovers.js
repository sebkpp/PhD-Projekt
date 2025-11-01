import { useEffect, useState } from 'react'
import { fetchHandovers } from '../services/trialOverviewService'

export function useHandovers(trialId, interval = 5000, enabled = true) {
    const [handovers, setHandovers] = useState([])

    useEffect(() => {
        if (!trialId || !enabled) return

        let isMounted = true

        const loadHandovers = () => {
            fetchHandovers(trialId)
                .then(data => {
                    if (isMounted) {
                        setHandovers(data)
                    }
                })
                .catch(err => console.error("Fehler beim Laden der Handovers:", err))
        }

        // Initiales Laden
        loadHandovers()

        // Polling starten
        const intervalId = setInterval(loadHandovers, interval)

        return () => {
            isMounted = false
            clearInterval(intervalId)
        }
    }, [trialId, interval, enabled])

    return { handovers, setHandovers }
}
