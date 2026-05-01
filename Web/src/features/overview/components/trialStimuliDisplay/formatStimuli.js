export function formatStimuli(trialConfigs, stimulusMap) {
    // Grundlegende Validierung
    if (!trialConfigs || !Array.isArray(trialConfigs) || !stimulusMap) {
        return [];
    }

    return trialConfigs.map(trial => {
        // Prüfe ob trial und trial.participants existieren
        if (!trial || !trial.participants) {
            return {
                trial_number: 0,
                participants: {}
            };
        }

        // Sichere Verarbeitung der Teilnehmer
        const formattedParticipants = {};
        Object.entries(trial.participants).forEach(([slotId, participant]) => {
            if (!participant) return;

            formattedParticipants[slotId] = {
                participant_id: participant.participant_id,
                avatar: participant.avatar,
                stimuli: {
                    vis: participant.selectedStimuli?.vis ? stimulusMap[participant.selectedStimuli.vis] : '—',
                    aud: participant.selectedStimuli?.aud ? stimulusMap[participant.selectedStimuli.aud] : '—',
                    tak: participant.selectedStimuli?.tac ? stimulusMap[participant.selectedStimuli.tac] : '—'
                }
            };
        });

        return {
            trial_number: trial.trial_number || 0,
            participants: formattedParticipants
        };
    });
}