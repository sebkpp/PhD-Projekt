import { useEffect, useState, useRef } from 'react'

export function useQuestionnaireCompletionStatus(experimentId, participantId, trialId, questionnaireNames) {
    const [completedCount, setCompletedCount] = useState(0)
    const [totalCount, setTotalCount] = useState(questionnaireNames.length)
    const [loading, setLoading] = useState(true)
    const intervalRef = useRef(null)

    useEffect(() => {
        setTotalCount(questionnaireNames.length)
        setLoading(true)

        async function fetchStatus() {
            let count = 0
            for (const name of questionnaireNames) {
                const res = await fetch(
                    `/api/questionnaire-responses?participant_id=${participantId}&trial_id=${trialId}&questionnaire_name=${encodeURIComponent(name)}`
                )
                if (res.ok) {
                    const data = await res.json()
                    if (data.data && Object.keys(data.data).length > 0) {
                        count++
                    }
                }
            }
            setCompletedCount(count)
            setLoading(false)

            // Stoppe das Intervall, wenn alle Fragebögen ausgefüllt sind
            if (count === questionnaireNames.length && intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
        }

        if (participantId && trialId && questionnaireNames.length > 0) {
            fetchStatus()
            if (!intervalRef.current) {
                intervalRef.current = setInterval(fetchStatus, 5000)
            }
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
        }
    }, [participantId, trialId, questionnaireNames.join(',')])

    const isLoading = loading && completedCount < totalCount


    return { completedCount, totalCount, loading: isLoading }
}