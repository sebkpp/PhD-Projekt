import HandoverTableRow from './HandoverTableRow'

export default function HandoverTable({ handovers }) {
    return (
        <div className="border border-border rounded-xl p-6 overflow-x-auto">
            <h2 className="text-xl font-semibold mb-4">Handover-Interaktionen</h2>

            {handovers.length === 0 ? (
                <p className="text-sm text-gray-400">Noch keine Übergaben erfolgt.</p>
            ) : (
                <table className="w-full text-sm text-left text-foreground border-separate border-spacing-y-2">
                    <thead className="text-xs uppercase text-gray-100 bg-gray-700/80 border-b border-gray-700 shadow-md sticky top-0">
                    <tr>
                        <th className="px-2 py-2 text-left w-10 font-semibold">#</th>
                        <th className="px-2 py-2 text-left w-32 font-semibold">Object</th>
                        <th className="px-2 py-2 text-center w-12 font-semibold">Giver</th>
                        <th className="px-2 py-2 text-center w-12 font-semibold">Receiver</th>
                        <th className="px-2 py-2">
                            <div className="grid grid-cols-4 gap-1 justify-items-center font-semibold">
                                <span>P1</span>
                                <span>P2</span>
                                <span>P3</span>
                                <span>Σ</span>
                            </div>
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                    {handovers.map((entry, index) => (
                        <HandoverTableRow key={index} entry={entry} index={index} />
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
