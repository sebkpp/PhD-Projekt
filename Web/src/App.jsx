import { useEffect, useState } from 'react'
import PlayerStatus from './components/participantStatus.jsx'

const playerSlots = [
    { id: 1, label: 'Proband 1' },
    { id: 2, label: 'Proband 2' }
]

function App() {
    const [players, setPlayers] = useState({
        1: { ready: true }
    })

    return (
        <main className="bg-background text-foreground min-h-screen w-full flex items-center justify-center p-4 sm:p-6 lg:p-8">
            <div className=" w-full max-w-md">
                <PlayerStatus players={players} playerSlots={playerSlots} />
            </div>
        </main>
    )
}

export default App
