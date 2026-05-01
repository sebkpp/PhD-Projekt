import { useState, useEffect } from 'react'
import HandoverSimulator from "@/debug/HandoverSimulator.jsx";
import ParticipantJoinSimulator from "@/debug/ParticipantJoinSimulator.jsx";
import ParticipantReadinessSimulator from "@/debug/ParticipantReadinessSimulator.jsx";

export default function SimulatorController() {
    const [currentTrialId, setCurrentTrialId] = useState(null)
    const [participantIds, setParticipantIds] = useState([]);

    useEffect(() => {
        const fetchCurrentTrialId = async () => {
            try {
                const res = await fetch('/api/trial/current_trial')
                if (res.ok) {
                    const data = await res.json()
                    setCurrentTrialId(data.trial_id)
                }
            } catch (e) {
                console.error(e)
            }
        }
        fetchCurrentTrialId()
    }, [])

    useEffect(() => {
        if (!currentTrialId) return;
        const fetchParticipantIds = async () => {
            try {
                const res = await fetch(`/api/trial/${currentTrialId}/participants`);
                if (res.ok) {
                    const data = await res.json();
                    // Angenommen, die Teilnehmer sind als Array von Objekten mit id
                    setParticipantIds(data.map(p => p.participant_id));
                }
            } catch (e) {
                console.error(e);
            }
        };
        fetchParticipantIds();
    }, [currentTrialId]);

    return (
        <div className="p-4 space-y-4">
            <div className="flex gap-4">
                <ParticipantJoinSimulator />
                <ParticipantReadinessSimulator />
            </div>
            <HandoverSimulator currentTrialId={currentTrialId} participantIds={participantIds} />
        </div>
    )
}
