export async function createExperiment({ name, description, researcher }) {
    const res = await fetch('/api/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, researcher })
    })

    if (!res.ok) {
        throw new Error('Fehler beim Anlegen des Experiments.')
    }

    return res.json()
}