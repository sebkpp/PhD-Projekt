import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function useSyncTrialIdInUrl(trialId) {
    const navigate = useNavigate()

    useEffect(() => {
        if (trialId) {
            const params = new URLSearchParams(window.location.search)
            params.set('trial', trialId)
            navigate(`${window.location.pathname}?${params.toString()}`, { replace: true })
        }
    }, [trialId, navigate])
}