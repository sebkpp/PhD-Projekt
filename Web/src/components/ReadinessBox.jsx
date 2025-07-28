export default function ReadinessBox({ players }) {
    return (
        <div className="border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Bereitschaft der Probanden</h2>
            <div className="flex gap-6">
                {[1, 2].map(id => {
                    const ready = players[id]?.ready === true
                    return (
                        <div key={id} className="flex-1 border border-border rounded p-3">
                            <strong className="block mb-1">Proband {id}</strong>
                            <div>Bereit: {ready ? '🟢 ja' : '🔴 nein'}</div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
