import { useAllPlayersReady } from '../../hooks/useAllParticipantsReady'

export default function ParticipantReadinessPanel({ players, participants }) {
    const allReady = useAllPlayersReady(players)

    return (
        <div className="border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Bereitschaft der Probanden</h2>
            <div className="flex gap-6">
                {[1, 2].map(id => {
                    const ready = players[id]?.ready === true
                    return (
                        <div
                            key={id}
                            className={`flex-1 border rounded p-3 ${
                                ready ? 'border-green-500 bg-green-900/20' : 'border-border'
                            }`}
                        >
                            <strong className="block mb-1">Proband {id}</strong>
                            <div>
                                Bereitschaft:{' '}
                                <span className={ready ? 'text-green-400' : 'text-red-400'}>
                                    {ready ? '🟢 ja' : '🔴 nein'}
                                </span>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
