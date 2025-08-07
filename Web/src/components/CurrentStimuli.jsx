export default function CurrentStimuliBox({ stimuli }) {
    return (
        <div className="border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">Aktuelle Stimuli</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(stimuli).map(([id, stim]) => (
                    <div key={id}>
                        <h3 className="font-semibold text-lg mb-2 text-accent">
                            Proband {id}
                        </h3>
                        <ul className="text-sm space-y-1">
                            <li>
                                <span className="font-medium text-gray-400">Visuell:</span>{' '}
                                {stim.vis || '—'}
                            </li>
                            <li>
                                <span className="font-medium text-gray-400">Auditiv:</span>{' '}
                                {stim.aud || '—'}
                            </li>
                            <li>
                                <span className="font-medium text-gray-400">Taktil:</span>{' '}
                                {stim.tak || '—'}
                            </li>
                        </ul>
                    </div>
                ))}
            </div>
        </div>
    )
}
