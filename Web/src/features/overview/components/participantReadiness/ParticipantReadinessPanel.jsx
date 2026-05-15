import { useTranslation } from 'react-i18next';
import { useAllPlayersReady } from '../../hooks/useAllParticipantsReady'

export default function ParticipantReadinessPanel({ players, participants }) {
    const { t } = useTranslation('overview');
    const allReady = useAllPlayersReady(players)

    return (
        <div className="border border-border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">{t('readiness.title')}</h2>
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
                            <strong className="block mb-1">{t('readiness.participant', { id })}</strong>
                            <div>
                                {t('readiness.label')}{' '}
                                <span className={ready ? 'text-green-400' : 'text-red-400'}>
                                    {ready ? t('readiness.ready') : t('readiness.notReady')}
                                </span>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
