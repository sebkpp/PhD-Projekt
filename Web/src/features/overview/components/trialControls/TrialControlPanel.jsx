import { useAllPlayersReady } from '../../hooks/useAllParticipantsReady.js'
import { useQuestionnairesDone } from '../../hooks/useQuestionnairesDone.js'

export default function TrialControlPanel({
                                              players,
                                              onStart,
                                              onEnd,
                                              trialRunning,
                                              disableStart,
                                              isDemographyDone,
                                              currentTrialNumber,
                                              totalTrials,
                                              completedTrials,
                                              participants,
                                              prevTrialId
}) {
    const allReady = useAllPlayersReady(players)
    const allQuestionnairesDone = useQuestionnairesDone(participants, prevTrialId)
    const isStartDisabled = !allReady || trialRunning || disableStart || !allQuestionnairesDone || !isDemographyDone || (completedTrials === totalTrials && totalTrials > 0);
    let statusMessages = [];

    if (!isDemographyDone) {
        statusMessages = [
            <span className="text-yellow-300">
            Der Trial kann erst gestartet werden, wenn beide Probanden den Demographie-Fragebogen ausgefühlt haben und bereit sind.
        </span>
        ];
    }
    else {
    if (completedTrials === totalTrials && totalTrials > 0) {
        // Nur diese Meldung anzeigen, wenn alle Trials beendet sind
        statusMessages.push(<span>✅ Alle Trials wurden beendet.</span>);
    } else if (trialRunning) {
        // Nur diese Meldung, wenn ein Trial läuft
        statusMessages.push(
            <span>
            ▶️ Trial {currentTrialNumber} von {totalTrials} läuft...{' '}
                <small className="text-gray-400">({`trial_id: ???`})</small>
        </span>
        );
    } else if (completedTrials > 0 && completedTrials !== totalTrials) {
        // Nur diese Meldung, wenn ein Trial gerade beendet wurde
        statusMessages.push(
            <span>⏹️ Trial {completedTrials} von {totalTrials} beendet.</span>
        );
        if (!allQuestionnairesDone) {
            statusMessages.push(<span>⏳ Warte, bis alle Fragebögen abgeschlossen sind.</span>);
        }
    } else if (!allReady && !trialRunning) {
        statusMessages.push(<span>⏳ Warte, bis beide Probanden bereit sind.</span>);
    } else if (!allQuestionnairesDone) {
        statusMessages.push(<span>⏳ Warte, bis alle Fragebögen abgeschlossen sind.</span>);
    } else if (!trialRunning && allReady && allQuestionnairesDone) {
        statusMessages.push(<span>✅ Beide Probanden sind bereit. Du kannst den Trial starten.</span>);
    }
    }


    return (
        <div className="border border-border rounded-xl p-6">
            <div className="flex flex-col gap-4">
                <div className="text-sm md:text-base text-gray-300 text-center">
                    {statusMessages.map((msg, i) => <div key={i}>{msg}</div>)}
                </div>

                <button
                    onClick={onStart}
                    disabled={isStartDisabled}
                    className="px-6 py-3 w-full bg-accent text-white rounded hover:bg-green-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    ▶️ Trial starten
                </button>

                <button
                    onClick={onEnd}
                    disabled={!trialRunning}
                    className="px-6 py-3 w-full bg-red-500 text-white rounded hover:bg-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    ⏹️ Trial beenden
                </button>
            </div>
        </div>
    )
}
