import { useMemo } from 'react'
import { formatStimuli } from './formatStimuli'

export function useFormattedStimuli(trialConfigs, stimulusMap) {
    return useMemo(() => formatStimuli(trialConfigs, stimulusMap), [trialConfigs, stimulusMap])
}
