export default function HandoverTable({ handovers }) {
    return (
        <div className="border border-border rounded-xl p-6 overflow-x-auto">
            <h2 className="text-xl font-semibold mb-4">Handover-Interaktionen</h2>

            {handovers.length === 0 ? (
                <p className="text-sm text-gray-400">Noch keine Übergaben erfolgt.</p>
            ) : (
                <table className="w-full text-sm text-left text-foreground border-separate border-spacing-y-2">
                    <thead className="text-xs uppercase text-gray-400">
                    <tr>
                        <th className="px-2">#</th>
                        <th className="px-2">Object</th>
                        <th>Giver</th>
                        <th>Reciever</th>
                        <th>Phase 1 (ms)</th>
                        <th>Phase 2 (ms)</th>
                        <th>Overall (ms)</th>
                    </tr>
                    </thead>
                    <tbody>
                    {handovers.map((entry, index) => {
                        const total = (entry.phase1 || 0) + (entry.phase2 || 0)
                        return (
                            <tr key={index} className="border-b border-border">
                                <td className="px-2">{index + 1}</td>
                                <td className="px-2">{entry.object}</td>
                                <td>{entry.giver}</td>
                                <td>{entry.receiver}</td>
                                <td>{entry.phase1}</td>
                                <td>{entry.phase2}</td>
                                <td>{total}</td>
                            </tr>
                        )
                    })}
                    </tbody>
                </table>
            )}
        </div>
    )
}
