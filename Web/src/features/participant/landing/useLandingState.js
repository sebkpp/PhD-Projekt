import { useState } from 'react'
import {useNavigate, useParams, useSearchParams} from 'react-router-dom'

export function useLandingState() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { studyId, experimentId } = useParams()
    const slot = searchParams.get('slot')
    const trial_id = searchParams.get('trial')

    const handleStartDemography = () => {

        navigate(`/study/${studyId}/experiment/${experimentId}/participantdemography?slot=${slot}&trial=${trial_id}`)
    }

    return {
        experimentId,
        slot,
        handleStartDemography,
    }
}
