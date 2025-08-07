import { useEffect, useState } from 'react'
import { fetchAvatarOptions } from './avatarOptionService'

export function useAvatarOptions() {
    const [avatarOptions, setAvatarOptions] = useState([])
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchAvatarOptions()
            .then(setAvatarOptions)
            .catch(err => {
                console.error(err)
                setError(err)
            })
    }, [])

    return { avatarOptions, error }
}
