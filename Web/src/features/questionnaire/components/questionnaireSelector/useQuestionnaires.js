import { useEffect, useState } from 'react'
import { getAllQuestionnaires } from './questionnaireService.js'

export function useQuestionnaires() {
    const [allQuestionnaires, setAllQuestionnaires] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function load() {
            try {
                const data = await getAllQuestionnaires()
                setAllQuestionnaires(data)
            } catch (e) {
                console.error("Fehler beim Laden der Fragebögen", e)
                setError(e)
            } finally {
                setLoading(false)
            }
        }
        load()
    }, [])

    return { allQuestionnaires, loading, error }
}
