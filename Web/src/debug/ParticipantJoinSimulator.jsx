import { useState, useRef, useEffect } from "react"
import { useTranslation } from 'react-i18next'

const PLAYERS = [
    { id: "1", n: 1 },
    { id: "2", n: 2 },
]

export default function ParticipantJoinSimulator() {
    const { t } = useTranslation('debug')
    const [status, setStatus] = useState({ "1": "disconnected", "2": "disconnected" })
    const heartbeatRefs = useRef({ "1": null, "2": null })

    useEffect(() => {
        return () => Object.values(heartbeatRefs.current).forEach(id => { if (id) clearInterval(id) })
    }, [])

    const joinPlayer = async (playerId) => {
        setStatus(s => ({ ...s, [playerId]: "connecting" }))
        try {
            const res = await fetch('/api/participants/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            })
            if (res.ok) {
                setStatus(s => ({ ...s, [playerId]: "connected" }))
                heartbeatRefs.current[playerId] = setInterval(() => sendHeartbeat(playerId), 2000)
            } else {
                setStatus(s => ({ ...s, [playerId]: "error" }))
            }
        } catch {
            setStatus(s => ({ ...s, [playerId]: "error" }))
        }
    }

    const sendHeartbeat = async (playerId) => {
        try {
            await fetch('/api/participants/heartbeat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            })
        } catch { /* ignore */ }
    }

    const leavePlayer = (playerId) => {
        if (heartbeatRefs.current[playerId]) {
            clearInterval(heartbeatRefs.current[playerId])
            heartbeatRefs.current[playerId] = null
        }
        setStatus(s => ({ ...s, [playerId]: "disconnected" }))
    }

    return (
        <div className="flex flex-col gap-3">
            {PLAYERS.map(({ id, n }) => {
                const s = status[id]
                const connected = s === "connected"
                const connecting = s === "connecting"
                const error = s === "error"
                return (
                    <div key={id} className={`flex items-center justify-between rounded-lg px-4 py-3 border transition-colors ${
                        connected ? 'border-green-700 bg-green-900/20' : error ? 'border-red-700 bg-red-900/20' : 'border-gray-700 bg-gray-800/50'
                    }`}>
                        <div className="flex items-center gap-2">
                            <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                                connected ? 'bg-green-400 animate-pulse' : connecting ? 'bg-yellow-400 animate-pulse' : error ? 'bg-red-400' : 'bg-gray-500'
                            }`} />
                            <span className="text-sm font-medium">{t('connection.participant', { n })}</span>
                            <span className="text-xs text-gray-500">
                                {connected ? t('connection.connected') : connecting ? t('connection.connecting') : error ? t('connection.error') : t('connection.disconnected')}
                            </span>
                        </div>
                        <button
                            onClick={() => connected ? leavePlayer(id) : joinPlayer(id)}
                            disabled={connecting}
                            className={`text-xs px-3 py-1.5 rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                                connected ? 'bg-red-700 hover:bg-red-600 text-white' : 'bg-blue-700 hover:bg-blue-600 text-white'
                            }`}
                        >
                            {connected ? t('connection.disconnectButton') : t('connection.connectButton')}
                        </button>
                    </div>
                )
            })}
            <p className="text-xs text-gray-500 leading-relaxed">{t('connection.heartbeatInfo')}</p>
        </div>
    )
}
