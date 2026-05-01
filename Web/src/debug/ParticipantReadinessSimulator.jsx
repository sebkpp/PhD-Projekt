import { useState, useEffect } from "react";

export default function ParticipantReadinessSimulator() {
    const [readiness, setReadiness] = useState({});
    const slots = [1, 2];

    const fetchReadiness = async () => {
        try {
            const res = await fetch('/api/participants/readiness_status');
            if (res.ok) {
                const data = await res.json();
                setReadiness(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const setParticipantReady = async (slot, ready) => {
        try {
            const res = await fetch('/api/participants/readiness_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slot, ready })
            });
            if (res.ok) fetchReadiness();
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchReadiness();
    }, []);



    return (
        <div className="space-y-4">
            {slots.map(slot =>  {
                const isReady = !!readiness[slot];

                return (
                <div key={slot} className="flex items-center gap-2">
                    <button
                        onClick={() => setParticipantReady(slot, !isReady)}
                        className={`px-4 py-2 rounded ${isReady ? "bg-green-600" : "bg-yellow-600"} text-white`}
                    >
                        {isReady ? "Bereitschaft entfernen" : "Bereitschaft setzen"}                    </button>
                    <span className={isReady ? "text-green-400" : "text-red-400"}>
                        {isReady ? "✅ bereit" : "❌ nicht bereit"}
                    </span>
                </div>
                );
            })}
        </div>
    );
}