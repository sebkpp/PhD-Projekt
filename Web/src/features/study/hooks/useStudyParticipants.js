import { useEffect, useState } from 'react'
import { fetchParticipants } from '../services/studyService.js'

export function useStudyParticipants(studyId) {
    const [participants, setParticipants] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!studyId) return
        setLoading(true)
        setError(null)
        fetchParticipants(studyId)
            .then(data => setParticipants(data || []))
            .catch(err => setError(err))
            .finally(() => setLoading(false))
    }, [studyId])

    return { participants, loading, error }
}