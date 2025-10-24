import {useCallback, useEffect, useState} from 'react'
import {loadAndSortTrials, loadStimulusMap} from "../services/trialOverviewService.js";

export function useTrialOverviewData(experimentId) {
    const [stimulusMap, setStimulusMap] = useState({})
    const [trialConfigs, setTrialConfigs] = useState([])
    const [status, setStatus] = useState({ participants: [] })

    const reloadTrialData = useCallback(async () => {
        const data = await loadAndSortTrials(experimentId)
        setTrialConfigs(data)
    }, [experimentId])

    // Load and sort Trial-Infos
    useEffect(() => {
        loadAndSortTrials(experimentId)
            .then(setTrialConfigs)
            .catch(err => console.error("Fehler beim Laden der Trial-Daten:", err))
    }, [experimentId])

    // Load Stimuli
    useEffect(() => {
        loadStimulusMap()
            .then(setStimulusMap)
            .catch(err => console.error("Fehler beim Laden der Stimuli:", err))
    }, [])

    useEffect(() => {
        reloadTrialData()
    }, [reloadTrialData])

    return {
        trialConfigs,
        reloadTrialData,
        stimulusMap,
        status,
        setStatus,
    }
}
