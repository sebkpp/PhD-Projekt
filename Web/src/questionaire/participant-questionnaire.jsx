import { useNavigate, useSearchParams } from 'react-router-dom'
import { useState } from 'react'

export default function ParticipantQuestionnaire() {
    const navigate = useNavigate()
    const [params] = useSearchParams()
    const experimentId = parseInt(params.get('experiment'))
    const slot = params.get('slot')

    const [age, setAge] = useState('')
    const [gender, setGender] = useState('')
    const [handedness, setHandedness] = useState('')
    const [submitted, setSubmitted] = useState(false)

    // Neue Fehlerobjekte
    const [errors, setErrors] = useState({
        age: false,
        gender: false,
        handedness: false
    })

    const handleSubmit = async () => {
        const newErrors = {
            age: !age || isNaN(parseInt(age)) || parseInt(age) < 18 || parseInt(age) > 100,
            gender: !gender,
            handedness: !handedness
        }

        setErrors(newErrors)

        // Wenn irgendein Fehler vorhanden ist → abbrechen
        if (Object.values(newErrors).some(Boolean)) return

        const payload = {
            experiment_id: experimentId,
            age: parseInt(age),
            gender,
            handedness
        }

        try {
            const res = await fetch('/api/participants', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (res.ok) {
                const data = await res.json()
                const participant_id = data.participant_id
                setSubmitted(true)
                await fetch('/api/participants/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ slot, participant_id })
                })

                navigate(`/participant/waiting?experiment=${experimentId}&slot=${slot}&participant=${participant_id}`)
            } else {
                alert('Fehler beim Absenden. Bitte erneut versuchen.')
            }
        } catch (err) {
            alert('Verbindungsfehler. Bitte später erneut versuchen.')
        }
    }

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
                            className={`w-full bg-gray-800 border rounded px-3 py-2 ${
                                errors.age ? 'border-red-500' : 'border-border'
                            }`}
                        />
                        {errors.age && (
                            <p className="text-red-400 text-sm mt-1">
                                Bitte gib ein Alter zwischen 18 und 100 ein.
                            </p>
                        )}
                    </div>

                    {/* Geschlecht */}
                    <div>
                        <label className="block font-semibold mb-1">Geschlecht</label>
                        <select
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                            className={`w-full bg-gray-800 border rounded px-3 py-2 ${
                                errors.gender ? 'border-red-500' : 'border-border'
                            }`}
                        >
                            <option value="">Bitte auswählen</option>
                            <option value="male">Männlich</option>
                            <option value="female">Weiblich</option>
                            <option value="diverse">Divers</option>
                        </select>
                        {errors.gender && (
                            <p className="text-red-400 text-sm mt-1">Bitte wähle ein Geschlecht aus.</p>
                        )}
                    </div>

                    {/* Händigkeit */}
                    <div>
                        <label className="block font-semibold mb-1">Händigkeit</label>
                        <select
                            value={handedness}
                            onChange={(e) => setHandedness(e.target.value)}
                            className={`w-full bg-gray-800 border rounded px-3 py-2 ${
                                errors.handedness ? 'border-red-500' : 'border-border'
                            }`}
                        >
                            <option value="">Bitte auswählen</option>
                            <option value="right">Rechtshändig</option>
                            <option value="left">Linkshändig</option>
                            <option value="ambi">Beidhändig</option>
                        </select>
                        {errors.handedness && (
                            <p className="text-red-400 text-sm mt-1">Bitte wähle eine Händigkeit aus.</p>
                        )}
                    </div>

                    <button
                        onClick={handleSubmit}
                        className="mt-4 px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition-all w-full"
                    >
                        Absenden
                    </button>
                </div>
            </div>
        </div>
    )
}
