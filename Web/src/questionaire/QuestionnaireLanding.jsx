import { useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function ProbandLanding() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()

    const experimentId = searchParams.get('experiment')
    const slot = searchParams.get('slot')

    const [demographyDone, setDemographyDone] = useState(false)
    const [ready, setReady] = useState(false)
    const [trialId, setTrialId] = useState(null)

    useEffect(() => {
        if (!experimentId || !slot) return

        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/active-questionnaire?experiment=${experimentId}&slot=${slot}`)
                if (res.ok) {
                    const data = await res.json()
                    if (data?.type === 'nasatlx') {
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
    }, [experimentId, slot])

    const handleStart = () => {
        if (ready && trialId !== null) {
            navigate(`/participant/${experimentId}/${slot}/nasatlx?trial=${trialId}`)
        }
    }

    useEffect(() => {
        if (!demographyDone || !experimentId || !slot) return

        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/active-questionnaire?experiment=${experimentId}&slot=${slot}`)
                if (res.ok) {
                    const data = await res.json()
                    if (data?.type === 'nasatlx') {
                        setReadyForNext(true)
                        setTrialId(data.trialId)
                        clearInterval(interval)
                    }
                }
            } catch (err) {
                console.error('Fehler beim Abrufen des Fragebogenstatus:', err)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [demographyDone, experimentId, slot])

    const handleStartDemography = () => {
        navigate(`/participant/demography?experiment=${experimentId}&slot=${slot}`)
    }

    const handleStartNext = () => {
        navigate(`/participant/${experimentId}/${slot}/nasatlx?trial=${trialId}`)
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4 text-center relative">
            {/* Info oben rechts */}
            <div className="absolute top-4 right-4 text-sm text-gray-500">
                Experiment: <span className="font-mono text-gray-300">{experimentId}</span><br />
                Slot: <span className="font-mono text-gray-300">{slot}</span>
            </div>

            <h1 className="text-2xl font-bold mb-4">Willkommen zum Experiment</h1>

            {!demographyDone && (
                <>
                    <p className="text-lg text-gray-400 max-w-md mb-6">
                        Bitte beginnen Sie mit dem kurzen Demographie-Fragebogen.
                    </p>
                    <button
                        onClick={handleStartDemography}
                        className="px-6 py-3 bg-accent text-white rounded hover:bg-accent/80 transition"
                    >
                        📋 Demographie starten
                    </button>
                </>
            )}

            {demographyDone && !readyForNext && (
                <>
                    <p className="text-lg text-gray-400 max-w-md">
                        Vielen Dank! Bitte warten Sie, bis der Versuchsleiter den nächsten Fragebogen freischaltet.
                        Sobald dieser bereit ist, erscheint ein Button zum Fortfahren.
                    </p>
                    <div className="mt-6 animate-pulse text-accent text-4xl">⏳</div>
                </>
            )}

            {demographyDone && readyForNext && (
                <div className="flex flex-col items-center gap-4">
                    <p className="text-lg text-accent font-semibold max-w-md">
                        Der nächste Fragebogen ist bereit. Bitte klicken Sie auf den Button, um fortzufahren.
                    </p>
                    <button
                        onClick={handleStartNext}
                        className="mt-4 px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition"
                    >
                        🚀 NASA-TLX starten
                    </button>
                </div>
            )}
        </div>
    )
}