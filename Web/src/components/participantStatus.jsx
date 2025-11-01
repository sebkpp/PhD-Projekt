import {useEffect, useState} from "react";

export default function PlayerStatus({playerSlots }) {

    const [players, setPlayers] = useState({
        1: { connected: false },
        2: { connected: false }
    })

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                // Verbindungsstatus abrufen
                const connRes = await fetch('/api/participants/connection_status');
                const connData = connRes.ok ? await connRes.json() : {};

                // Bereitschaftsstatus abrufen
                const readyRes = await fetch('/api/participants/readiness_status');
                const readyData = readyRes.ok ? await readyRes.json() : {};

                setPlayers({
                    1: { connected: connData["1"], ready: readyData["1"] },
                    2: { connected: connData["2"], ready: readyData["2"] }
                });
            } catch (err) {
                console.error('Status konnte nicht abgerufen werden:', err);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, []);


    return (
        <div className="flex items-center gap-6 h-10">
            {playerSlots.map(({ id, label }) => {
                const player = players[id] || {};
                return (
                    <div key={id} className="flex items-center gap-2 text-sm">
                        <span className="font-semibold text-gray-100">{label}:</span>
                        <span className={player.connected ? 'text-green-500' : 'text-red-500'} title="Verbindung">
                            {player.connected ? '🟢' : '🔴'}
                        </span>
                        <span className="mx-1 text-gray-400">|</span>
                        <span className={player.ready ? 'text-green-400' : 'text-red-400'} title="Bereitschaft">
                            {player.ready ? '✅' : '❌'}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}
