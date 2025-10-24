import {useState} from 'react'
import {areAllQuestionnairesInTrialDone} from "../services/trialOverviewService.js";
import {usePolling} from "./usePooling.js";

export function useQuestionnairesDone(participants, prevTrialId) {
    const [allDone, setAllDone] = useState(!prevTrialId)

    usePolling(async () => {
        if (!prevTrialId || !participants?.length) {
            setAllDone(!prevTrialId)
            return
        }
        try {
            const done = await areAllQuestionnairesInTrialDone(participants, prevTrialId)
            setAllDone(done)
        } catch {
            setAllDone(false)
        }
    }, [participants, prevTrialId, allDone], 2000,() => allDone )


    return allDone
}