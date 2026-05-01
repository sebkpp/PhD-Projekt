export function Loading() {
    return <p>Lädt Fragebögen...</p>
}
export function Error({ message }) {
    return <p className="text-red-500">Fehler: {message}</p>
}
export function NoQuestionnaires() {
    return <p>Keine Fragebögen verfügbar.</p>
}