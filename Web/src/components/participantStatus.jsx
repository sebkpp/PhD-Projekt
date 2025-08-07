import {useEffect, useState} from "react";


export default function PlayerStatus({playerSlots }) {

    const [players, setPlayers] = useState({
        1: { connected: false },
        2: { connected: false }
    })

    useEffect(() => {
        const fetchConnectionStatus = async () => {
            try {
                const res = await fetch('/api/participants/connection_status')
                if (res.ok) {
                    const data = await res.json()
                    setPlayers({
                        1: { connected: data["1"] },
                        2: { connected: data["2"] }
                    })
                }
            } catch (err) {
                console.error('Verbindungsstatus konnte nicht abgerufen werden:', err)
            }
        }

        fetchConnectionStatus()
        const interval = setInterval(fetchConnectionStatus, 2000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="border border-border rounded-xl p-4">
            <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold whitespace-nowrap">Verbindungsstatus:</h2>
                <div className="flex gap-4">
                    {playerSlots.map(({ id, label }) => {
                        const player = players[id];
                        const connected = player ? player.connected : false;
                        return (
                            <div key={id} className="flex items-center gap-2">
                                <h3 className="font-semibold text-accent">{label}:</h3>
                                <div className="text-sm">
                                    {connected ? <span className="text-green-500">🟢 verbunden</span> : <span className="text-red-500">🔴 getrennt</span>}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
