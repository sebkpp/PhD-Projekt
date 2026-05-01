export function validateTrialConfigs(trialConfigs, status) {
    const errors = []

    if (!status[1]?.participant_id || !status[2]?.participant_id) {
        errors.push({
            field: 'questionnaire',
            message: 'Beide Probanden müssen den Fragebogen ausgefüllt haben.'
        })
    }

    trialConfigs.forEach((trial, trialIndex) => {
        for (const id of [1, 2]) {
            const participant = trial[id]
            const stimuli = participant?.stimuli || {}
            const selected = participant?.selectedStimuli || {}
            const avatar = participant?.avatar || ''

            if (!avatar) {
                errors.push({
                    trialIndex,
                    participant_id: id,
                    field: 'avatar',
                    message: `Trial ${trialIndex + 1}, Proband ${id}: Es muss eine Avatarsichtbarkeit ausgewählt werden.`
                })
            }

            const hasActiveStimulus = Object.values(stimuli).some(v => v === true)
            if (!hasActiveStimulus) {
                errors.push({
                    trialIndex,
                    participant_id: id,
                    field: 'stimuli',
                    message: `Trial ${trialIndex + 1}, Proband ${id}: Es muss mindestens ein Stimulus-Typ aktiviert sein.`
                })
            }

            for (const type of Object.keys(stimuli)) {
                if (stimuli[type] && !selected[type]) {
                    errors.push({
                        trialIndex,
                        participant_id: id,
                        field: `stimuli.${type}`,
                        message: `Trial ${trialIndex + 1}, Proband ${id}: Für aktivierten Stimulus "${type.toUpperCase()}" fehlt die spezifische Auswahl.`
                    })
                }
            }
        }
    })

    return errors
}
