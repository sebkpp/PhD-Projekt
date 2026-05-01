import { useState, useEffect } from 'react'
import {getStudyQuestionnaires} from '../service/questionnaireFlowService'

export function useStudyQuestionnaires(study_id) {
    const [questionnaires, setQuestionnaires] = useState([])
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!study_id) {
            setQuestionnaires([]);
            setError(null)
            setLoading(false)
            return;
        }

        setLoading(true)
        getStudyQuestionnaires(study_id)
            .then(data => {
                setQuestionnaires(data || [])
                setError(null)
            })
            .catch(err => setError(err.message || 'Unbekannter Fehler'))
            .finally(() => setLoading(false))
    }, [study_id])


    return { questionnaires, loading, error}
}
