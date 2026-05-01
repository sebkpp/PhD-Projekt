import { useParams  } from 'react-router-dom'
import { usePhase } from '../../components/PhaseProvider.jsx'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

import HandoverTable from "./components/handover/HandoverTable.jsx";
import TrialStimuliDisplay from './components/trialStimuliDisplay/TrialStimuliDisplay.jsx'
import TrialControlPanel from './components/trialControls/TrialControlPanel.jsx'
import ParticipantReadinessPanel from './components/participantReadiness/ParticipantReadinessPanel.jsx'

import { useTrialOverviewData } from './hooks/useTrialOverviewData.js'
import { useTrialController } from './hooks/useTrialController.js'
import { useHandovers } from "./hooks/useHandovers.js";
import { useTrialPhaseHandlers } from './hooks/usePhaseHandlers'
import { usePrevTrialInfo } from './hooks/usePrevTrialInfo.js'
import QuestionnaireQrGroup from "@/features/overview/components/QRCode/ParticipantStartQRCodeGroup.jsx";
import {useEffect, useState} from "react";
import {useAllDemographyDone} from "@/features/overview/hooks/useAllDemographyDone.js";
import {useParticipantsForExperiment} from "@/features/overview/hooks/useParticipantsForExperiment.js";

function TrialOverview() {
    const { studyId, experimentId } = useParams()
    const { setCurrentPhase, setCompletedTrials, setTotalTrials } = usePhase()
    const { participants, loading: participantsLoading, error: participantsError } = useParticipantsForExperiment(experimentId)
    // load trial data and status
    const { trialConfigs, reloadTrialData,  stimulusMap, status, setStatus } = useTrialOverviewData(experimentId)

    // trial controls
    const {
        currentTrialId,
        currentTrialNumber,
        nextTrialNumber,
        trialRunning,
        startTrial,
        finishTrial,
    } = useTrialController(trialConfigs, setStatus, reloadTrialData)


    const { handovers, setHandovers } = useHandovers(currentTrialId, 5000, trialRunning)

    const isLastTrial = trialConfigs.length === 0 || nextTrialNumber > trialConfigs.length;
    const completedTrials = Math.min(nextTrialNumber - 1, trialConfigs.length);

    const prevTrialId = usePrevTrialInfo(trialConfigs, nextTrialNumber)

    const { handleStartTrial, handleEndTrial } = useTrialPhaseHandlers({
        startTrial,
        finishTrial,
        setCurrentPhase,
        setCompletedTrials,
        nextTrialNumber,
        trialConfigs,
        participants,
        experimentId
    })

    // Dummy-Daten
    const playersReady = {
        1: { ready: true },
        2: { ready: true }
    }
    const demographyDone = useAllDemographyDone(participants, experimentId)

    useEffect(() => {
        setTotalTrials(trialConfigs.length)
    }, [trialConfigs])


    const [qrCollapsed, setQrCollapsed] = useState(false);


    return (
        <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 auto-rows-min">
                <div className="col-span-2">
                    <div className="w-full flex justify-center">
                        <button
                            className="w-full flex items-center justify-center bg-gray-100 dark:bg-gray-700 border-b border-gray-300 dark:border-gray-600 py-2 transition hover:bg-gray-200 dark:hover:bg-gray-600"
                            onClick={() => setQrCollapsed((prev) => !prev)}
                            aria-expanded={!qrCollapsed}
                        >
                            {qrCollapsed
                                ? <ChevronDownIcon className="w-6 h-6 text-gray-800 dark:text-gray-100" />
                                : <ChevronUpIcon className="w-6 h-6 text-gray-800 dark:text-gray-100" />
                            }
                        </button>
                    </div>
                    <div
                        className="w-full transition-[max-height] duration-500 overflow-hidden"
                        style={{
                            maxHeight: qrCollapsed ? 0 : '1000px',
                        }}
                    >
                        <div
                            className="px-6 pb-6 pt-2 transition-opacity duration-300"
                            style={{
                                opacity: qrCollapsed ? 0 : 1,
                            }}
                        >
                            <QuestionnaireQrGroup
                                experiment_id={experimentId}
                                study_id={studyId}
                                status={status}
                                trialId={currentTrialId}
                            />
                        </div>
                    </div>
                </div>


                    {/* Linke Spalte: TrialControlPanel + TrialStimuliDisplay */}
                    <div className="flex flex-col gap-6">
                        <TrialControlPanel
                            players={playersReady}
                            onStart={handleStartTrial}
                            onEnd={handleEndTrial}
                            trialRunning={trialRunning}
                            disableStart={isLastTrial}
                            isDemographyDone={demographyDone}
                            currentTrialNumber={trialRunning ? currentTrialNumber : nextTrialNumber}
                            totalTrials={trialConfigs.length}
                            completedTrials={completedTrials}
                            participants={participants}
                            prevTrialId={prevTrialId}
                        />
                        <TrialStimuliDisplay
                            trialConfigs={trialConfigs}
                            stimulusMap={stimulusMap}
                            participants={status.participants}
                            currentTrialIndex={(trialRunning ? currentTrialNumber : nextTrialNumber) - 1}
                        />
                    </div>
                    {/* Rechte Spalte: HandoverTable */}
                    <div>
                        <HandoverTable handovers={handovers} />
                    </div>
        </div>
        </>
    )
}

export default TrialOverview
