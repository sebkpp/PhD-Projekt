export async function fetchStimuliOptions() {
    const res = await fetch('/api/stimuli')
    if (!res.ok) throw new Error('Fehler beim Laden der Stimuli')
    const data = await res.json()

    const grouped = { vis: [], aud: [], tak: [] }
    const typeMap = { visual: 'vis', auditory: 'aud', tactile: 'tak' }

    data.forEach(s => {
        const key = typeMap[s.type]
        if (key) grouped[key].push({ value: s.id, label: s.name })
    })

    return grouped
}
