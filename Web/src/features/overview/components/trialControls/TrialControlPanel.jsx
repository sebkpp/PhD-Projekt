import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation('overview');
    const allReady = useAllPlayersReady(players)
    const allQuestionnairesDone = useQuestionnairesDone(participants, prevTrialId)
    const isStartDisabled = !allReady || trialRunning || disableStart || !allQuestionnairesDone || !isDemographyDone || (completedTrials === totalTrials && totalTrials > 0);
    let statusMessages = [];

    if (!isDemographyDone) {
        statusMessages = [
            <span className="text-yellow-300">
            {t('control.demographyPending')}
        </span>
        ];
    }
    else {
    if (completedTrials === totalTrials && totalTrials > 0) {
        // Nur diese Meldung anzeigen, wenn alle Trials beendet sind
        statusMessages.push(<span>{t('control.allTrialsFinished')}</span>);
    } else if (trialRunning) {
        // Nur diese Meldung, wenn ein Trial läuft
        statusMessages.push(
            <span>
            {t('control.trialRunning', { current: currentTrialNumber, total: totalTrials })}{' '}
                <small className="text-gray-400">({`trial_id: ???`})</small>
        </span>
        );
    } else if (completedTrials > 0 && completedTrials !== totalTrials) {
        // Nur diese Meldung, wenn ein Trial gerade beendet wurde
        statusMessages.push(
            <span>{t('control.trialEnded', { completed: completedTrials, total: totalTrials })}</span>
        );
        if (!allQuestionnairesDone) {
            statusMessages.push(<span>{t('control.waitingQuestionnaires')}</span>);
        }
    } else if (!allReady && !trialRunning) {
        statusMessages.push(<span>{t('control.waitingBothReady')}</span>);
    } else if (!allQuestionnairesDone) {
        statusMessages.push(<span>{t('control.waitingQuestionnaires')}</span>);
    } else if (!trialRunning && allReady && allQuestionnairesDone) {
        statusMessages.push(<span>{t('control.readyToStart')}</span>);
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
                    {t('control.startTrial')}
                </button>

                <button
                    onClick={onEnd}
                    disabled={!trialRunning}
                    className="px-6 py-3 w-full bg-red-500 text-white rounded hover:bg-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    {t('control.endTrial')}
                </button>
            </div>
        </div>
    )
}
