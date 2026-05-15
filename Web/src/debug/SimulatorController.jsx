import { useState, useEffect, useCallback } from 'react'
import HandoverSimulator from "@/debug/HandoverSimulator.jsx"
import ParticipantJoinSimulator from "@/debug/ParticipantJoinSimulator.jsx"
import ParticipantReadinessSimulator from "@/debug/ParticipantReadinessSimulator.jsx"
import { useTranslation } from 'react-i18next'

export default function SimulatorController() {
    const { t } = useTranslation('debug')
    const [currentTrialId, setCurrentTrialId] = useState(null)
    const [participantIds, setParticipantIds] = useState([])

    const fetchTrialState = useCallback(async () => {
        try {
            const res = await fetch('/api/trials/current')
            if (!res.ok) return
            const data = await res.json()
            setCurrentTrialId(data.trial_id ?? null)
        } catch { /* ignore */ }
    }, [])

    const fetchParticipants = useCallback(async () => {
        if (!currentTrialId) return
        try {
            const res = await fetch(`/api/trials/${currentTrialId}/participants`)
            if (!res.ok) return
            const data = await res.json()
            setParticipantIds(data.map(p => p.participant_id))
        } catch { /* ignore */ }
    }, [currentTrialId])

    useEffect(() => {
        fetchTrialState()
        const id = setInterval(fetchTrialState, 3000)
        return () => clearInterval(id)
    }, [fetchTrialState])

    useEffect(() => {
        if (!currentTrialId) { setParticipantIds([]); return }
        fetchParticipants()
        const id = setInterval(fetchParticipants, 5000)
        return () => clearInterval(id)
    }, [currentTrialId, fetchParticipants])

    const trialActive = currentTrialId !== null

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">{t('controller.title')}</h1>
                    <p className="text-sm text-gray-400 mt-0.5">{t('controller.subtitle')}</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchTrialState}
                        className="px-3 py-1.5 text-xs rounded bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-colors"
                    >
                        {t('controller.refresh')}
                    </button>
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
                        trialActive
                            ? 'bg-green-900/50 text-green-300 border border-green-700'
                            : 'bg-gray-800 text-gray-400 border border-gray-700'
                    }`}>
                        <span className={`w-2 h-2 rounded-full ${trialActive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
                        {trialActive
                            ? t('controller.trialActive', { id: currentTrialId })
                            : t('controller.noTrial')}
                    </span>
                </div>
            </div>

            {!trialActive && (
                <div className="mb-6 px-4 py-3 rounded-lg bg-yellow-900/30 border border-yellow-700/50 text-yellow-300 text-sm">
                    ⚠ {t('controller.noTrialWarning')}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <SimCard title={t('controller.panels.connection')} icon="🔌" description={t('controller.panels.connectionDesc')}>
                    <ParticipantJoinSimulator />
                </SimCard>
                <SimCard title={t('controller.panels.readiness')} icon="✅" description={t('controller.panels.readinessDesc')}>
                    <ParticipantReadinessSimulator />
                </SimCard>
                <SimCard
                    title={t('controller.panels.handover')}
                    icon="🤝"
                    description={t('controller.panels.handoverDesc')}
                    disabled={!trialActive}
                    disabledHint={t('controller.panels.waitingForTrial')}
                >
                    <HandoverSimulator currentTrialId={currentTrialId} participantIds={participantIds} />
                </SimCard>
            </div>
        </div>
    )
}

function SimCard({ title, icon, description, children, disabled = false, disabledHint }) {
    return (
        <div className={`rounded-xl border p-5 flex flex-col gap-4 ${
            disabled ? 'border-gray-800 bg-gray-900/40 opacity-60' : 'border-gray-700 bg-gray-900'
        }`}>
            <div>
                <h2 className="text-base font-semibold flex items-center gap-2"><span>{icon}</span>{title}</h2>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">{description}</p>
                {disabled && disabledHint && <p className="text-xs text-yellow-500 mt-1">{disabledHint}</p>}
            </div>
            <div className={disabled ? 'pointer-events-none' : ''}>{children}</div>
        </div>
    )
}
