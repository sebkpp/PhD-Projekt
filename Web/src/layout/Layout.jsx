import { Outlet } from 'react-router-dom'
import Timeline from '../components/Timeline.jsx'
import PlayerStatus from '../components/participantStatus.jsx'

export default function Layout({ playerSlots }) {
    return (
        <main className="bg-background text-foreground min-h-screen p-6">
            <div className="max-w-6xl mx-auto space-y-6">
                <Timeline/>
                <PlayerStatus playerSlots={playerSlots} />
                <Outlet context={{  }}/>
            </div>
        </main>
    )
}

