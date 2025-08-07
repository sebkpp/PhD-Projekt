export default function ParticipantQuestionnaireForm({
                                                         age,
                                                         setAge,
                                                         gender,
                                                         setGender,
                                                         handedness,
                                                         setHandedness,
                                                         loading,
                                                         error,
                                                         submitted,
                                                         onSubmit,
                                                     }) {
    if (submitted) {
        return (
            <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
                <h1 className="text-2xl font-bold mb-4">Vielen Dank!</h1>
                <p>Deine Angaben wurden gespeichert.</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
            <div className="max-w-xl w-full">
                <h1 className="text-2xl font-bold mb-6 text-center">Teilnehmer-Fragebogen</h1>
                <p className="text-sm text-gray-400 text-center mb-8">
                    Bitte beantworte die folgenden Angaben. Deine Teilnahme bleibt anonym.
                </p>

                <div className="space-y-6">
                    {/* Alter */}
                    <div>
                        <label className="block font-semibold mb-1">Alter</label>
                        <input
                            type="number"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        />
                    </div>

                    {/* Geschlecht */}
                    <div>
                        <label className="block font-semibold mb-1">Geschlecht</label>
                        <select
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        >
                            <option value="">Bitte auswählen</option>
                            <option value="male">Männlich</option>
                            <option value="female">Weiblich</option>
                            <option value="diverse">Divers</option>
                        </select>
                    </div>

                    {/* Händigkeit */}
                    <div>
                        <label className="block font-semibold mb-1">Händigkeit</label>
                        <select
                            value={handedness}
                            onChange={(e) => setHandedness(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        >
                            <option value="">Bitte auswählen</option>
                            <option value="right">Rechtshändig</option>
                            <option value="left">Linkshändig</option>
                            <option value="ambi">Beidhändig</option>
                        </select>
                    </div>

                    {error && (
                        <p className="text-red-400 text-sm mt-1 text-center">
                            {error}
                        </p>
                    )}

                    <button
                        onClick={onSubmit}
                        disabled={loading}
                        className="mt-4 px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition-all w-full"
                    >
                        {loading ? "Absenden..." : "Absenden"}
                    </button>
                </div>
            </div>
        </div>
    )
}
