import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchActiveQuestionnaire } from './landingService'

export function useLandingState() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()

    const experiment_id = searchParams.get('experiment')
    const slot = searchParams.get('slot')

    const [demography_done, setDemographyDone] = useState(false)
    const [nasatlx_ready, setNasaTlxReady] = useState(false)
    const [trial_id, setTrialId] = useState(null)

    useEffect(() => {
        if (!experiment_id || !slot || !demography_done) return

        const interval = setInterval(async () => {
            try {
                const data = await fetchActiveQuestionnaire(experiment_id, slot)
                if (data?.type === 'nasatlx') {
                    setNasaTlxReady(true)
                    setTrialId(data.trial_id)
                    clearInterval(interval)
                }
            } catch (e) {
                console.error('Fehler beim Abrufen des Fragebogenstatus:', e)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [experiment_id, slot, demography_done])

    const handleStartDemography = () => {
        navigate(`/participant/demography?experiment=${experiment_id}&slot=${slot}`)
    }

    const handleStartNasaTlx = () => {
        if (trial_id) {
            navigate(`/participant/${experiment_id}/${slot}/nasatlx?trial=${trial_id}`)
        }
    }

    return {
        experiment_id,
        slot,
        demography_done,
        setDemographyDone,
        nasatlx_ready,
        handleStartDemography,
        handleStartNasaTlx,
    }
}
