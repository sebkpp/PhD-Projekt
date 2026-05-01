export async function fetchStimuliOptions() {
    const res = await fetch('/api/stimuli')
    if (!res.ok) throw new Error('Fehler beim Laden der Stimuli')
    const data = await res.json()

    const grouped = {}

    data.forEach(s => {
        if (!grouped[s.type]) grouped[s.type] = [];
        grouped[s.type].push({ value: s.id, label: s.name });
    })

    return grouped
}
