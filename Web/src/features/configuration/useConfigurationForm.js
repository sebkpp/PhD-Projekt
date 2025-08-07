import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchParticipantStatus, submitTrialConfiguration, getConnectionStatus  } from './configurationService'
import { validateTrialConfigs } from './configurationValidation'
const MAX_TRIALS = 10

export function useConfigurationForm(experimentId, setCurrentPhase) {
    const navigate = useNavigate()

    const [trialConfigs, setTrialConfigs] = useState([
        { 1: { stimuli: {}, selectedStimuli: {}, avatar: '' },
            2: { stimuli: {}, selectedStimuli: {}, avatar: '' } }
    ])
    const [activeIndex, setActiveIndex] = useState(0)
    const [validationErrors, setValidationErrors] = useState([])
    const [status, setStatus] = useState({
        1: { submitted: false, participant_id: null },
        2: { submitted: false, participant_id: null }
    })

    const [connectionStatus, setConnectionStatus] = useState({ 1: false, 2: false })
    const bothConnected = connectionStatus["1"] && connectionStatus["2"]

    const handleChange = (participantId, field, value) => {
        const updated = [...trialConfigs]
        updated[activeIndex] = {
            ...updated[activeIndex],
            [participantId]: {
                ...updated[activeIndex][participantId],
                [field]: value
            }
        }
        setTrialConfigs(updated)
    }

    const handleNext = async () => {
        const errors = validateTrialConfigs(trialConfigs, status)
        if (errors.length > 0) {
            setValidationErrors(errors)
            return
        }

        setValidationErrors([])

        try {
            await submitTrialConfiguration(experimentId, trialConfigs, status)
            setCurrentPhase('Warten auf Probanden')
            navigate(`/experiment/${experimentId}/overview`)
        } catch (e) {
            alert(e.message || 'Fehler beim Absenden der Konfiguration')
        }
    }

    useEffect(() => {
        setStatus({
            1: { submitted: false, participant_id: null },
            2: { submitted: false, participant_id: null }
        })
    }, [experimentId])

    useEffect(() => {
        if (!experimentId) return

        const interval = setInterval(async () => {
            try {
                const [status1, status2] = await Promise.all([
                    fetchParticipantStatus(experimentId, 1),
                    fetchParticipantStatus(experimentId, 2)
                ])
                setStatus({ 1: status1, 2: status2 })
            } catch (e) {
                console.error('Status-Fehler:', e)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [experimentId])


    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const result = await getConnectionStatus()
                setConnectionStatus(result)
            } catch (e) {
                console.error(e)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [])


    return {
        trialConfigs, setTrialConfigs,
        activeIndex, setActiveIndex,
        validationErrors, setValidationErrors,
        handleChange,
        handleNext,
        status,
        bothConnected,
        MAX_TRIALS
    }
}
