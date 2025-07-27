export default function PlayerStatus({ players, playerSlots }) {
    return (
        <div className="border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Probanden</h2>

            {playerSlots.map(({ id, label }) => {
                const player = players[id]
                const connected = !!player
                const ready = player?.ready === true

                return (
                    <div key={id} className="mb-4 pb-2 border-b border-border">
                        <strong className="block">{label}</strong>
                        <div>Status: {connected ? '🟢 verbunden' : '🔴 getrennt'}</div>
                        <div>Bereitschaft: {ready ? '🟢 bereit' : '🔴 nicht bereit'}</div>
                    </div>
                )
            })}
        </div>
    )
}