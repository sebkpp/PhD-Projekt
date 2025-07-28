import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import ConfigPage from './pages/ConfigPage.jsx'
import TrialOverview from "./pages/TrialOverview.jsx";

export default function AppRouter() {
    const players = {
        1: { connected: true },
        2: { connected: true }
    }

    const playerSlots = [
        { id: 1, label: 'Proband 1' },
        { id: 2, label: 'Proband 2' }
    ]

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout players={players} playerSlots={playerSlots} />}>
                    <Route index element={<ConfigPage />} />
                    <Route path="konfiguration" element={<ConfigPage />} />
                    <Route path="trial" element={<TrialOverview />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}
