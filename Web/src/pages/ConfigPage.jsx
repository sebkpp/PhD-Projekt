import { useState } from 'react'
import {useNavigate, useOutletContext} from 'react-router-dom'
import ParticipantConfigBox from '../components/ParticipantConfigurationBox.jsx'
import { usePhase } from '../components/PhaseProvider.jsx'

export default function ConfigPage() {
    const { setCurrentPhase } = usePhase()
    const navigate = useNavigate()
    const {players} = useOutletContext()

    const [configs, setConfigs] = useState({
        1: { stimuli: {}, selectedStimuli: {}, avatar: '' },
        2: { stimuli: {}, selectedStimuli: {}, avatar: '' }
    })

    // Beispiel: Hier bekommst du den Verbindungsstatus aus dem Backend
    const connectedPlayers = Object.keys(players).filter(id => players[id].connected);

    const bothConnected = connectedPlayers.length === 2

    const handleNext = () => {
        // TODO: Optional validieren
        setCurrentPhase('Warten auf Probanden')  // Phase global umschalten
        navigate('/trial')                      // zur nächsten Seite springen
    }



    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Versuchs-Konfiguration</h1>

            {!bothConnected && (
                <p className="text-red-400 mb-4">
                    ⚠️ Beide Probanden müssen verbunden sein, bevor konfiguriert werden kann.
                </p>
            )}

            <ParticipantConfigBox configs={configs} setConfigs={setConfigs} disabled={!bothConnected} />

            <div className="mt-8">
                <button
                    onClick={handleNext}
                    disabled={!bothConnected}
                    className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 disabled:opacity-50">
                    ➡️ Weiter zu „Warten auf Probanden“
                </button>
            </div>
        </div>
    )
}
