import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createExperiment } from './experimentService'

export function useExperimentForm() {
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [researcher, setResearcher] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const navigate = useNavigate()

    const handleSubmit = async () => {
        if (!name.trim()) {
            setError('Bitte gib einen Namen für das Experiment ein.')
            return
        }

        setLoading(true)
        setError(null)

        try {
            const data = await createExperiment({ name, description, researcher })
            navigate(`/experiment/${data.experiment_id}/configure`)
        } catch (e) {
            console.error(e)
            setError(e.message || 'Unbekannter Fehler')
        } finally {
            setLoading(false)
        }
    }

    return {
        name, setName,
        description, setDescription,
        researcher, setResearcher,
        loading,
        error,
        handleSubmit
    }
}
