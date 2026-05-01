import {useEffect, useRef, useState} from 'react'
import {
    getTrialsForExperiment
} from '../service/questionnaireFlowService.js'
import {getTrialById} from "@/features/overview/services/trialOverviewService.js";

export function useQuestionnaireAvailability({ studyId, experimentId, participantId, trialId}) {
    const [ready, setReady] = useState(false)
    const [error, setError] = useState(null)
    const intervalRef = useRef(null)
    const [currentTrialId, setCurrentTrialId] = useState(trialId)

    useEffect(() => {
        if (!experimentId || !trialId || ready) return

        intervalRef.current = setInterval(async () => {
            try {
                //const trials = await getTrialsForExperiment(experimentId)
                //const currentTrial = trials.find(trial => trial.trial_id == trialId)
                //console.log("Trials", trials, "currentTrial", currentTrial)
                const currentTrial = await getTrialById(trialId)
                if (!currentTrial) throw new Error('Trial nicht gefunden')
                if (currentTrial.is_finished) {
                    setReady(true)
                    clearInterval(intervalRef.current)
                }
            } catch (err) {
                setError(err.message)
            }
        }, 2000)

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, [experimentId, trialId, ready])

    return { trialId: currentTrialId, ready, error }
}
