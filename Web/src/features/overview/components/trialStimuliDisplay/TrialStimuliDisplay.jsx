import { useFormattedStimuli } from './useFormatStimuli.js'
import TrialStimuliBox from './TrialStimuliBox.jsx'

export default function TrialStimuliDisplay({ trialConfigs, stimulusMap, participants, currentTrialIndex }) {
    //const formattedTrials = useFormattedStimuli(trialConfigs, stimulusMap);
    if (!trialConfigs.length || !stimulusMap) {
        return null;
    }

    const currentTrial = trialConfigs[currentTrialIndex];
    const nextTrial = currentTrialIndex < trialConfigs.length - 1
        ? trialConfigs[currentTrialIndex + 1]
        : null;

    if (!currentTrial && !nextTrial) {
        return (
            <div className="p-4 text-center text-gray-500">
                Alle Trials beendet.
            </div>
        );
    }

    return (
        <div className="border border-border rounded-xl p-6 space-y-6">
            {currentTrial && (
                <TrialStimuliBox
                    trialNumber={currentTrial.trial_number}
                    slots={currentTrial.slots}
                    title="Aktueller Trial"
                    highlight={true}
                />
            )}

            {nextTrial && (
                <TrialStimuliBox
                    trialNumber={nextTrial.trial_number}
                    slots={nextTrial.slots}
                    title="Nächster Trial"
                />
            )}
        </div>
    );
}
