import { useState, useEffect } from 'react'
import {
    startTrial as apiStartTrial,
    endTrial as apiEndTrial,
} from '../services/trialOverviewService.js'

export function useTrialController(trialConfigs, setStatus, reloadTrialData) {
    const allTrialsFinished = trialConfigs.length > 0 && trialConfigs.every(trial => trial.is_finished);
    const nextTrialNumber = allTrialsFinished
        ? trialConfigs.length + 1
        : (trialConfigs.findIndex(trial => !trial.is_finished) + 1);
    const [currentTrialNumber, setCurrentTrialNumber] = useState(null)
    const [currentTrialId, setCurrentTrialId] = useState(null)
    const [trialRunning, setTrialRunning] = useState(false)

    // Aktualisiere currentTrialId und Status basierend auf currentTrialNumber / nextTrialNumber
    useEffect(() => {
        const displayedTrialNumber = currentTrialNumber !== null ? currentTrialNumber : Math.max(nextTrialNumber - 1, 1)
        const displayedTrial = trialConfigs.find(t => t.trial_number === displayedTrialNumber)
        if (displayedTrial) {
            setCurrentTrialId(displayedTrial.trial_id)
            setStatus({
                participants: (displayedTrial.slots || []).map(slot => ({
                    slot: slot.slot,
                    trial_slot_id: slot.trial_slot_id,
                    stimuli: slot.stimuli,
                })),
            })
        } else {
            setCurrentTrialId(null)
            setStatus({ participants: [] })
        }
    }, [trialConfigs, currentTrialNumber, nextTrialNumber, setStatus])

    async function startTrial() {
        if (!trialConfigs.length) return
        const trialToStart = trialConfigs.find(t => t.trial_number === nextTrialNumber)
        if (!trialToStart) return

        try {
            await apiStartTrial(trialToStart.trial_id)
            setCurrentTrialNumber(nextTrialNumber)
            setTrialRunning(true)
        } catch (error) {
            console.error("Fehler beim Starten des Trials:", error)
        }
    }

    async function finishTrial() {
        if (!trialConfigs.length || currentTrialNumber === null) return
        const trialToEnd = trialConfigs.find(t => t.trial_number === currentTrialNumber)
        if (!trialToEnd) return

        try {
            await apiEndTrial(trialToEnd.trial_id)
            setTrialRunning(false)
            setCurrentTrialNumber(null)
            if (reloadTrialData) {
                await reloadTrialData()
            }
        } catch (error) {
            console.error("Fehler beim Beenden des Trials:", error)
        }
    }

    return {
        currentTrialId,
        currentTrialNumber,
        nextTrialNumber,
        trialRunning,
        startTrial,
        finishTrial,
    }
}
