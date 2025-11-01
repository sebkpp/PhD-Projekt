export async function fetchAvatarOptions() {
    const res = await fetch('/api/avatar-visibility')
    if (!res.ok) throw new Error('Fehler beim Laden der Avatare')
    const data = await res.json()

    return data.map(opt => ({ value: opt.id, label: opt.label }))
}