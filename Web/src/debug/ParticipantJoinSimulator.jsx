import { useState, useRef, useEffect } from "react";

export default function ParticipantJoinSimulator() {
    const [connected1, setConnected1] = useState(false);
    const [connected2, setConnected2] = useState(false);

    const heartbeatInterval1 = useRef(null);
    const heartbeatInterval2 = useRef(null);

    const joinPlayer = async (playerId, setConnected, heartbeatRef) => {
        try {
            const res = await fetch('/api/participants/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            });
            if (res.ok) {
                setConnected(true);
                heartbeatRef.current = setInterval(() => sendHeartbeat(playerId), 2000);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const sendHeartbeat = async (playerId) => {
        try {
            await fetch('/api/participants/heartbeat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            });
        } catch (e) {
            console.error(e);
        }
    };

    const leavePlayer = async (playerId, setConnected, heartbeatRef) => {
        if (heartbeatRef.current) {
            clearInterval(heartbeatRef.current);
            heartbeatRef.current = null;
        }
        try {
            await fetch('/api/participants/mock_connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId, connected: false })
            });
        } catch (e) {
            console.error(e);
        }
        setConnected(false);
    };

    useEffect(() => {
        return () => {
            if (heartbeatInterval1.current) clearInterval(heartbeatInterval1.current);
            if (heartbeatInterval2.current) clearInterval(heartbeatInterval2.current);
        };
    }, []);

    return (
        <div className="space-y-4">
            <div>
                <button
                    onClick={() => connected1 ? leavePlayer("1", setConnected1, heartbeatInterval1) : joinPlayer("1", setConnected1, heartbeatInterval1)}
                    className="px-4 py-2 bg-blue-600 text-white rounded"
                >
                    {connected1 ? "Proband 1 trennen" : "Proband 1 verbinden"}
                </button>
            </div>
            <div>
                <button
                    onClick={() => connected2 ? leavePlayer("2", setConnected2, heartbeatInterval2) : joinPlayer("2", setConnected2, heartbeatInterval2)}
                    className="px-4 py-2 bg-green-600 text-white rounded"
                >
                    {connected2 ? "Proband 2 trennen" : "Proband 2 verbinden"}
                </button>
            </div>
        </div>
    );
}