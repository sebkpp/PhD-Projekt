import { useEffect, useRef } from 'react'

export function usePolling(callback, deps, intervalMs = 2000, shouldStop) {
    const intervalRef = useRef(null)

    useEffect(() => {
        let cancelled = false

        async function poll() {
            if (!cancelled) await callback()
            if (shouldStop()) {
                if (intervalRef.current) clearInterval(intervalRef.current)
                intervalRef.current = null
                cancelled = true
            }
        }

        intervalRef.current = setInterval(poll, intervalMs)
        poll()

        return () => {
            cancelled = true
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, deps)
}