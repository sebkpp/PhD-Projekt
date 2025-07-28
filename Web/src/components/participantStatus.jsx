export default function PlayerStatus({ players, playerSlots }) {
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
