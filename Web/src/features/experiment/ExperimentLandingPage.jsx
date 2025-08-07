import { useEffect } from 'react'
import ExperimentForm from './ExperimentForm'

export default function ExperimentLandingPage() {
    useEffect(() => {
        document.title = 'Neues Experiment';
    }, [])

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground p-6">
            <ExperimentForm />
        </div>
    )
}