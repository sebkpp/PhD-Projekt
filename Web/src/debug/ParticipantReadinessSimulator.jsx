import { useState, useEffect } from "react"

const SLOTS = [
    { slot: "1", label: "Proband 1" },
    { slot: "2", label: "Proband 2" },
]

export default function ParticipantReadinessSimulator() {
    const [readiness, setReadiness] = useState({})
    const [loading, setLoading] = useState(false)

    const fetchReadiness = async () => {
        try {
            const res = await fetch('/api/participants/readiness_status')
            if (res.ok) setReadiness(await res.json())
        } catch {
            // ignore
        }
    }

    const toggleReady = async (slot) => {
        const current = !!readiness[slot]
        setLoading(true)
        try {
            const res = await fetch('/api/participants/readiness_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slot, ready: !current })
            })
            if (res.ok) await fetchReadiness()
        } catch {
            // ignore
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchReadiness()
    }, [])

    return (
        <div className="flex flex-col gap-3">
            {SLOTS.map(({ slot, label }) => {
                const ready = !!readiness[slot]
                return (
                    <div
                        key={slot}
                        className={`flex items-center justify-between rounded-lg px-4 py-3 border transition-colors ${
                            ready
                                ? 'border-green-700 bg-green-900/20'
                                : 'border-gray-700 bg-gray-800/50'
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${ready ? 'bg-green-400' : 'bg-gray-500'}`} />
                            <span className="text-sm font-medium">{label}</span>
                            <span className={`text-xs ${ready ? 'text-green-400' : 'text-gray-500'}`}>
                                {ready ? 'bereit' : 'nicht bereit'}
                            </span>
                        </div>
                        <button
                            onClick={() => toggleReady(slot)}
                            disabled={loading}
                            className={`text-xs px-3 py-1.5 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                                ready
                                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                                    : 'bg-green-700 hover:bg-green-600 text-white'
                            }`}
                        >
                            {ready ? 'Bereitschaft entfernen' : 'Als bereit markieren'}
                        </button>
                    </div>
                )
            })}
        </div>
    )
}
