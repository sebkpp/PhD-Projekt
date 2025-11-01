import { useState, useCallback } from 'react'
import { closeStudy } from '@/features/study/services/studyService.js'

export function useCloseStudy(studyId) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [result, setResult] = useState(null)

    const close = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await closeStudy(studyId)
            setResult(res)
        } catch (err) {
            setError(err)
        } finally {
            setLoading(false)
        }
    }, [studyId])

    return { close, loading, error, result }
}