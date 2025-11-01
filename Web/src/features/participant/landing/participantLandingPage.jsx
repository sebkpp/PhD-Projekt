import { useLandingState } from './useLandingState'

export default function ParticipantLanding() {

    const {
        experimentId,
        slot,
        handleStartDemography,
    } = useLandingState()


    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4 text-center relative">
            {/* Info oben rechts */}
            <div className="absolute top-4 right-4 text-sm text-gray-500">
                Experiment: <span className="font-mono text-gray-300">{experimentId}</span><br />
                Slot: <span className="font-mono text-gray-300">{slot}</span>
            </div>

            <h1 className="text-2xl font-bold mb-4">Willkommen zum Experiment</h1>

            <>
                <p className="text-lg text-gray-400 max-w-md mb-6">
                    Bitte beginnen Sie mit dem kurzen Demographie-Fragebogen.
                </p>
                <button
                    onClick={handleStartDemography}
                    className="px-6 py-3 bg-accent text-white rounded hover:bg-accent/80 transition"
                >
                    Fragebogen starten
                </button>
            </>
        </div>
    )
}
