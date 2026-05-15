import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const OBJECTS = ["Würfel","Quader","Langer Quader","Flacher Quader","Bogen","Zylinder","Halber Zylinder","Dreieck"]

function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min }

export default function HandoverSimulator({ currentTrialId, participantIds }) {
    const { t } = useTranslation('debug')
    const [active, setActive] = useState(false)
    const [count, setCount] = useState(0)
    const [lastHandover, setLastHandover] = useState(null)
    const intervalRef = useRef(null)
    const canStart = currentTrialId !== null && participantIds.length >= 2

    const runHandover = async () => {
        const grasped_object = OBJECTS[randomInt(0, OBJECTS.length - 1)]
        const shuffled = [...participantIds].sort(() => Math.random() - 0.5)
        const giver = shuffled[0]
        const receiver = shuffled[1]
        const base = Date.now()
        const t2 = base + randomInt(200, 1200)
        const t3 = t2 + randomInt(200, 1200)
        const t4 = t3 + randomInt(200, 1200)
        try {
            const createRes = await fetch(`/api/handovers/trials/${currentTrialId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ giver, receiver, grasped_object })
            })
            if (!createRes.ok) return
            const { handover_id } = await createRes.json()
            await fetch(`/api/handovers/${handover_id}/phases`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    giver_grasped_object: new Date(base).toISOString(),
                    receiver_touched_object: new Date(t2).toISOString(),
                    receiver_grasped_object: new Date(t3).toISOString(),
                    giver_released_object: new Date(t4).toISOString(),
                })
            })
            setCount(c => c + 1)
            setLastHandover({ grasped_object, giver, receiver, handover_id })
        } catch { /* ignore */ }
    }

    const start = () => {
        if (!canStart) return
        setActive(true)
        intervalRef.current = setInterval(runHandover, 2000)
    }

    const stop = () => {
        setActive(false)
        if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    }

    useEffect(() => { if (!currentTrialId) stop(); return () => stop() }, [currentTrialId])

    return (
        <div className="flex flex-col gap-4">
            <div className="rounded-lg bg-gray-800/60 border border-gray-700 px-4 py-3 text-sm space-y-1">
                <div className="flex justify-between">
                    <span className="text-gray-400">{t('handover.trialId')}</span>
                    <span className="font-mono font-medium">
                        {currentTrialId ?? <span className="text-gray-500">–</span>}
                    </span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-400">{t('handover.participants')}</span>
                    <span className="font-mono font-medium">
                        {participantIds.length > 0 ? participantIds.join(', ') : <span className="text-gray-500">{t('handover.noParticipants')}</span>}
                    </span>
                </div>
            </div>
            {participantIds.length < 2 && currentTrialId !== null && (
                <p className="text-xs text-yellow-500">{t('handover.minParticipantsHint')}</p>
            )}
            <button
                onClick={active ? stop : start}
                disabled={!canStart}
                className={`w-full py-2.5 rounded-lg font-medium text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                    active ? 'bg-red-700 hover:bg-red-600 text-white' : 'bg-pink-700 hover:bg-pink-600 text-white'
                }`}
            >
                {active ? t('handover.stopButton') : t('handover.startButton')}
            </button>
            <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${active ? 'bg-pink-400 animate-pulse' : 'bg-gray-600'}`} />
                    <span className="text-gray-400">{t('handover.sent')}</span>
                    <span className="font-mono font-semibold">{count}</span>
                </div>
                {count > 0 && (
                    <button onClick={() => { setCount(0); setLastHandover(null) }} className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
                        {t('handover.reset')}
                    </button>
                )}
            </div>
            {lastHandover && (
                <div className="rounded-lg bg-gray-800/60 border border-gray-700 px-4 py-3 text-xs space-y-1">
                    <p className="text-gray-400 font-medium mb-1">{t('handover.lastHandover')}</p>
                    <div className="flex justify-between"><span className="text-gray-500">{t('handover.id')}</span><span className="font-mono">{lastHandover.handover_id}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">{t('handover.object')}</span><span>{lastHandover.grasped_object}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">{t('handover.giverReceiver')}</span><span className="font-mono">{lastHandover.giver} → {lastHandover.receiver}</span></div>
                </div>
            )}
        </div>
    )
}
