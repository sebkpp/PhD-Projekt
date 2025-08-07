import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createParticipant, submitParticipant } from './participantQuestionnaireService'

export function useParticipantQuestionnaire(experimentId, slot) {
    const [age, setAge] = useState('')
    const [gender, setGender] = useState('')
    const [handedness, setHandedness] = useState('')

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [submitted, setSubmitted] = useState(false)

    const navigate = useNavigate()

    const validate = () => {
        if (!age || isNaN(parseInt(age)) || parseInt(age) < 18 || parseInt(age) > 100)
            return 'Bitte gib ein Alter zwischen 18 und 100 ein.'
        if (!gender) return 'Bitte wähle ein Geschlecht aus.'
        if (!handedness) return 'Bitte wähle eine Händigkeit aus.'
        return null
    }

    const handleSubmit = async () => {
        const validationError = validate()
        if (validationError) {
            setError(validationError)
            return
        }

        setLoading(true)
        setError(null)

        try {
            const participantData = await createParticipant({
                experiment_id: experimentId,
                age: parseInt(age),
                gender,
                handedness,
            })

            await submitParticipant({
                slot,
                experiment_id: experimentId,
                participant_id: participantData.participant_id,
            })

            setSubmitted(true)
            navigate(`/participant/waiting?experiment=${experimentId}&slot=${slot}&participant=${participantData.participant_id}`)
        } catch (e) {
            setError(e.message || 'Fehler beim Absenden. Bitte erneut versuchen.')
        } finally {
            setLoading(false)
        }
    }

    return {
        age,
        setAge,
        gender,
        setGender,
        handedness,
        setHandedness,
        loading,
        error,
        submitted,
        handleSubmit,
    }
}
