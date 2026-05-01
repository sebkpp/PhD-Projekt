// src/debug/handoverSimulator.jsx
import React, { useRef, useEffect } from 'react'

export default function HandoverSimulator({ currentTrialId, participantIds }) {
    const [simActive, setSimActive] = React.useState(false)
    const intervalRef = useRef(null)

    const OBJECTS = [
        "Würfel",
        "Quader",
        "Langer Quader",
        "Flacher Quader",
        "Bogen",
        "Zylinder",
        "Halber Zylinder",
        "Dreieck"]

    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min
    }

    const startSim = () => {
        if (!currentTrialId) return
        setSimActive(true)
        intervalRef.current = setInterval(() => {
            const grasped_object = OBJECTS[getRandomInt(0, OBJECTS.length - 1)]
            const shuffled = [...participantIds].sort(() => Math.random() - 0.5)
            const giver = shuffled[0]
            const receiver = shuffled[1]
            // Basiszeitpunkt
            const base = Date.now()
            // Zufällige Zeitabstände (in ms)
            const t1 = base
            const t2 = base + getRandomInt(200, 1200)
            const t3 = t2 + getRandomInt(200, 1200)
            const t4 = t3 + getRandomInt(200, 1200)

            const handover = {
                grasped_object,
                giver_grasped_object: new Date(t1).toISOString(),
                receiver_touched_object: new Date(t2).toISOString(),
                receiver_grasped_object: new Date(t3).toISOString(),
                giver_released_object: new Date(t4).toISOString(),
                trial_id: currentTrialId,
                giver,
                receiver
            }
            fetch(`/api/trials/${currentTrialId}/handovers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(handover)
            }).catch(console.error)
        }, 2000)
    }

    const stopSim = () => {
        setSimActive(false)
        if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
        }
    }

    useEffect(() => {
        if (!currentTrialId) stopSim()
        return () => stopSim()
    }, [currentTrialId])


    return (
        <div className="mb-4">

            <div className="mb-2 px-3 py-2 bg-gray-900 rounded text-gray-200 flex gap-6 items-center">
            <span>
                <strong>Trial&nbsp;ID:</strong> {currentTrialId ?? <span className="text-gray-500">–</span>}
            </span>
                <span>
                <strong>Teilnehmer:</strong> {participantIds?.length > 0
                    ? participantIds.join(', ')
                    : <span className="text-gray-500">keine</span>}
            </span>
            </div>

            <button
                onClick={simActive ? stopSim : startSim}
                className={`px-4 py-2 rounded transition-colors duration-200
        ${!currentTrialId
                    ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                    : "bg-pink-600 text-white hover:bg-pink-700 cursor-pointer"
                }`}
                disabled={!currentTrialId}
            >
                {simActive ? "Stoppe Handover Simulation" : "Starte Handover Simulation"}
            </button>
        </div>
    )
}