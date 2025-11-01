import {useCallback, useEffect, useState} from 'react'
import { areAllQuestionnairesDone } from '../services/trialOverviewService.js'
import {usePolling} from "./usePooling.js";

export function useTrialPhaseHandlers({
                                          startTrial,
                                          finishTrial,
                                          setCurrentPhase,
                                          setCompletedTrials,
                                          nextTrialNumber,
                                          trialConfigs,
                                          participants,
                                          experimentId
}) {

    const prevTrialNumber = nextTrialNumber - 1
    const trialsExist = trialConfigs.length > 0
    const allTrialsFinished = trialsExist && nextTrialNumber > trialConfigs.length
    const [allQuestionnairesDone, setAllQuestionnairesDone] = useState(false)
    const participantIds = participants?.map(p => p.participant_id) ?? []

    usePolling(async () => {
        if (!allTrialsFinished) return
        const results = await Promise.all(
            participantIds.map(pid => areAllQuestionnairesDone(pid, experimentId))
        )
        const allDone = results.every(Boolean)

        setAllQuestionnairesDone(allDone)

    }, [allTrialsFinished, participants, experimentId, allQuestionnairesDone], 2000, () => allQuestionnairesDone )


    // Setze Phase auf "Beendet", wenn alle Fragebögen erledigt
    useEffect(() => {
        if (allTrialsFinished && allQuestionnairesDone) {
            setCurrentPhase('Beendet')
            setCompletedTrials(prevTrialNumber)
        }
    }, [allTrialsFinished, allQuestionnairesDone, setCurrentPhase, setCompletedTrials, prevTrialNumber])

    const handleStartTrial = useCallback(async () => {
        await startTrial()
        setCurrentPhase('Versuch')
    }, [startTrial, setCurrentPhase])

    const handleEndTrial = useCallback(async () => {
        await finishTrial()
        setCompletedTrials(prev => prev + 1)
        setCurrentPhase('Fragebogen')
    }, [finishTrial, setCompletedTrials, setCurrentPhase])

    return { handleStartTrial, handleEndTrial }
}