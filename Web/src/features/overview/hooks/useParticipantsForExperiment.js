import { useEffect, useState } from 'react'
import { getParticipantsForExperiment } from '../services/trialOverviewService.js'

export function useParticipantsForExperiment(experimentId) {
    const [participants, setParticipants] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!experimentId) return
        setLoading(true)
        getParticipantsForExperiment(experimentId)
            .then(setParticipants)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [experimentId])

    return { participants, loading, error }
}