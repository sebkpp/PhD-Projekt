import { useState } from 'react'

export function useQuestionnaireNavigator(length, onAllDone) {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [resetSignal, setResetSignal] = useState(0)

    const handleNext = async () => {
        setCurrentIndex(prevIndex => {
            if (prevIndex + 1 < length) {
                setResetSignal(s => s + 1)
                return prevIndex + 1
            }
            return prevIndex
        })

        if (currentIndex + 1 >= length) {
            await onAllDone()
        }
    }

    const reset = () => {
        setCurrentIndex(0)
        setResetSignal(s => s + 1)
    }

    return { currentIndex, resetSignal, handleNext, reset }
}