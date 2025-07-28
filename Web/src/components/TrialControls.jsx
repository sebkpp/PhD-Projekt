export default function TrialControls({ players, onStart, onEnd, trialRunning }) {
    const allReady = [1, 2].every(id => players[id]?.ready)

    return (
        <div className="border border-border rounded-xl p-6">
            <div className="flex flex-col gap-4">
                {/* Statusbereich */}
                <div className="text-sm md:text-base text-gray-300">
                    {allReady ? (
                        <span className="text-green-400 font-medium">
                            ✅ Beide Probanden sind bereit. Du kannst den Trial starten.
                        </span>
                    ) : (
                        <span className="text-yellow-300">
                            ⏳ Warte, bis beide Probanden bereit sind.
                        </span>
                    )}
                </div>

                {/* Start-Button */}
                <button
                    onClick={onStart}
                    disabled={!allReady || trialRunning}
                    className="px-6 py-3 w-full bg-accent text-white rounded hover:bg-green-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    ▶️ Trial starten
                </button>

                {/* Stop-Button */}
                <button
                    onClick={onEnd}
                    disabled={!trialRunning}
                    className="px-6 py-3 w-full bg-red-500 text-white rounded hover:bg-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    ⏹️ Trial beenden
                </button>
            </div>
        </div>
    );
}
