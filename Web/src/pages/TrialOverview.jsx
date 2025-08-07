import { usePhase } from '../components/PhaseProvider.jsx'
import { useNavigate, useParams  } from 'react-router-dom'
import ReadinessBox from '../components/ReadinessBox.jsx'
import TrialControls from '../components/TrialControls.jsx'
import HandoverTable from "../components/HandoverTable.jsx";
import CurrentStimuliBox from "../components/CurrentStimuli.jsx";
import QuestionnaireQrGroup from '../features/configuration/components/QuestionnaireQRCodeGroup.jsx'

import {useEffect, useState} from "react";

function TrialOverview() {
    const { experimentId } = useParams()
    const { setCurrentPhase } = usePhase()
    const navigate = useNavigate()

    const [stimulusMap, setStimulusMap] = useState({})

    const [trialConfigs, setTrialConfigs] = useState(null)
    const [trialRunning, setTrialRunning] = useState(false);

    const playersReady = {
        1: { ready: true },
        2: { ready: false }
    }

    useEffect(() => {
        fetch(`/api/experiments/${experimentId}/trials`)
            .then(res => res.json())
            .then(data => {
                const latestTrial = data[data.length - 1]
                setTrialConfigs(latestTrial.participants)
            })
            .catch(err => {
                console.error("Fehler beim Laden der Trial-Daten:", err)
            })
    }, [experimentId])

    useEffect(() => {
        fetch('/api/stimuli')
            .then(res => res.json())
            .then(data => {
                const map = {}
                data.forEach(stim => {
                    map[stim.id] = stim.name
                })
                setStimulusMap(map)
            })
            .catch(err => console.error("Fehler beim Laden der Stimuli:", err))
    }, [])

    const handleStartTrial = () => {
        setCurrentPhase('Trial läuft')
        setTrialRunning(true);
        navigate('/trial') // oder eine Seite für laufende Trials
    }

    const handleEndTrial = () => {
        setCurrentPhase('Trial beendet');
        setTrialRunning(false);
        navigate('/trial');
    }

    const [handovers, setHandovers] = useState([
        {
            object: 'Würfel A',
            giver: 'Proband 1',
            receiver: 'Proband 2',
            phase1: 530,
            phase2: 220
        },
        {
            object: 'Zylinder B',
            giver: 'Proband 2',
            receiver: 'Proband 1',
            phase1: 480,
            phase2: 310
        }
    ])

    const formatStimuli = (configs) => {
        const formatted = {}

        for (const [participantId, config] of Object.entries(configs)) {
            const selected = config.selectedStimuli || {}

            formatted[participantId] = {
                vis: stimulusMap[selected.vis] || '—',
                aud: stimulusMap[selected.aud] || '—',
                tak: stimulusMap[selected.tak] || '—'
            }
        }

        return formatted
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 auto-rows-min">
            <TrialControls players={playersReady} onStart={handleStartTrial} onEnd={handleEndTrial} trialRunning={trialRunning}/>
            <ReadinessBox players={playersReady} />

            {trialConfigs && <CurrentStimuliBox stimuli={formatStimuli(trialConfigs)} />}

            <div className="row-span-1">
                <HandoverTable handovers={handovers} />
            </div>

            <QuestionnaireQrGroup userIds={[104, 105]} trialId={3} />
        </div>
    )
}

export default TrialOverview
