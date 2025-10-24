import { useMemo } from 'react'

export function usePrevTrialInfo(trialConfigs, nextTrialNumber) {
    return useMemo(() => {

        const prevTrialNumber = nextTrialNumber - 1
        const prevTrial = trialConfigs.find(t => t.trial_number === prevTrialNumber)
        const prevTrialId = prevTrial ? prevTrial.trial_id : null

        return prevTrialId
    }, [trialConfigs, nextTrialNumber])
}