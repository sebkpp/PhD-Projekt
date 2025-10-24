import {useEffect, useRef, useState} from 'react'
import { getParticipantSubmissionStatus } from '@/features/participant/demography/participantQuestionnaireService.js'

export function useAllDemographyDone(participants, experimentId) {
    const [done, setAllDone] = useState(false)
    const participantIds = participants?.map(p => p.participant_id) ?? []
    const slots = [1, 2]
    const intervalRef = useRef(null)

    useEffect(() => {
        async function check() {
            let allDone = true
            for (const slot of slots) {
                const status = await getParticipantSubmissionStatus({ experiment_id: experimentId, slot })
                if (!status || Object.values(status)[0] !== true) {
                    allDone = false
                }
            }
            setAllDone(allDone)
            if (allDone && intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
        }
        check()
        if (!done && !intervalRef.current) {
            intervalRef.current = setInterval(check, 3000)
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
        }
    }, [participantIds, experimentId, done])

    return done
}