import { useEffect, useState } from 'react'
import { fetchStimuliOptions } from './stimuliOptionService'

export function useStimulusOptions() {
    const [stimulusOptions, setStimulusOptions] = useState({ vis: [], aud: [], tak: [] })
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchStimuliOptions()
            .then(setStimulusOptions)
            .catch(err => {
                console.error(err)
                setError(err)
            })
    }, [])

    return { stimulusOptions, error }
}
