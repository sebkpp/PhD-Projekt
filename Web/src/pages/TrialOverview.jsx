import { usePhase } from '../components/PhaseProvider.jsx'
import { useNavigate } from 'react-router-dom'
import ReadinessBox from '../components/ReadinessBox.jsx'
import TrialControls from '../components/TrialControls.jsx'
import HandoverTable from "../components/HandoverTable.jsx";
import CurrentStimuliBox from "../components/CurrentStimuli.jsx";
import {useState} from "react";

function TrialOverview() {
    const { setCurrentPhase } = usePhase()
    const navigate = useNavigate()
    const [trialRunning, setTrialRunning] = useState(false);

    const playersReady = {
        1: { ready: true },
        2: { ready: false }
    }

    const configs = {
        1: {
            stimuli: { vis: true, aud: false },
            avatar: 'hands',
            selectedStimuli: { vis: 'vis_color' }
        },
        2: {
            stimuli: { vis: true, aud: true },
            avatar: 'full',
            selectedStimuli: { vis: 'vis_inner', aud: 'aud_high' }
        }
    }

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

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 auto-rows-min">
            <TrialControls players={playersReady} onStart={handleStartTrial} onEnd={handleEndTrial} trialRunning={trialRunning}/>
            <ReadinessBox players={playersReady} />
            <CurrentStimuliBox stimuli={configs} />
            <div className="row-span-1">
                <HandoverTable handovers={handovers} />
            </div>
        </div>
    )
}

export default TrialOverview
