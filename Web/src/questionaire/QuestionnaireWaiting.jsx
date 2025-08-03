import { useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams  } from 'react-router-dom'

export default function ParticipantWaiting() {
    const [searchParams] = useSearchParams()
    const userId = searchParams.get('participant')
    const experimentId = searchParams.get('experiment')
    const slot = searchParams.get('slot')

    const navigate = useNavigate()
    const [ready, setReady] = useState(false)
    const [trialId, setTrialId] = useState(null)

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/active-questionnaire?user=${userId}`)
                if (res.ok) {
                    const data = await res.json()
                    console.log('Active questionnaire data:', data)
                    if (data?.type !== 'demography' && data?.trialId) {
                        // Wenn der Versuchsleiter weitere Fragebögen freigegeben hat
                        setReady(true)
                        setTrialId(data.trialId)
                        clearInterval(interval)
                    }
                }
            } catch (err) {
                console.error('Fehler beim Abrufen des Fragebogenstatus:', err)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [userId])

    const handleContinue = () => {
        if (ready && trialId !== null) {
            // Beispiel Weiterleitung zu NASA-TLX
            navigate(`/proband/${userId}/nasatlx?trial=${trialId}`)
        }
    }

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6 text-center">
            <h1 className="text-2xl font-bold mb-4">Vielen Dank für deine Angaben!</h1>

            {!ready && (
                <>
                    <p className="text-lg text-gray-400 max-w-md mb-6">
                        Bitte warte, bis der Versuchsleiter die weiteren Fragebögen bereitstellt.
                        Sobald diese verfügbar sind, kannst du fortfahren.
                    </p>
                    <div className="animate-pulse text-accent text-4xl">⏳</div>
                </>
            )}

            {ready && (
                <>
                    <p className="text-lg text-accent font-semibold max-w-md mb-4">
                        Die nächsten Fragebögen sind jetzt bereit.
                    </p>
                    <button
                        onClick={handleContinue}
                        className="px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition"
                    >
                        Weiter zum nächsten Fragebogen 🚀
                    </button>
                </>
            )}
        </div>
    )
}
