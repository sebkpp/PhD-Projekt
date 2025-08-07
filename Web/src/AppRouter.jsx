import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import ConfigPage from './features/configuration/ConfigPage.jsx'
import TrialOverview from "./pages/TrialOverview.jsx";
import NasaTLX from "./questionaire/nasaTLX.jsx";
import ExperimentLandingPage from './features/experiment/ExperimentLandingPage.jsx'

import ParticipantLanding from './features/participant/landing/ParticipantLandingPage.jsx'
import ParticipantQuestionnairePage from './features/participant/demography/ParticipantQuestionnairePage.jsx'
import ParticipantWaiting from "./questionaire/QuestionnaireWaiting.jsx";
import ParticipantJoinSimulator from './debug/ParticipantJoinSimulator.jsx'

export default function AppRouter() {
    const playerSlots = [
        { id: 1, label: 'Proband 1' },
        { id: 2, label: 'Proband 2' }
    ]

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ExperimentLandingPage />} />

                <Route element={<Layout playerSlots={playerSlots} />}>
                    <Route path="/experiment/:experimentId/configure" element={<ConfigPage />} />
                    <Route path="/experiment/:experimentId/overview" element={<TrialOverview />} />
                </Route>
                <Route path="/participant/start" element={<ParticipantLanding />} />
                <Route path="/participant/demography" element={<ParticipantQuestionnairePage />}/>
                <Route path="/participant/waiting" element={<ParticipantWaiting />} />
                <Route path="/participant/nasatlx" element={<NasaTLX />} />
                <Route path="/participant/join-simulator" element={<ParticipantJoinSimulator />} />

            </Routes>
        </BrowserRouter>
    )
}
