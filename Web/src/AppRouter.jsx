import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import ConfigPage from './pages/ConfigPage.jsx'
import TrialOverview from "./pages/TrialOverview.jsx";
import NasaTLX from "./questionaire/nasaTLX.jsx";
import QuestionnaireLanding from "./questionaire/QuestionnaireLanding.jsx";
import NewExperimentPage from './pages/ExperimentLandingPage.jsx'
import ParticipantQuestionnaire from "./questionaire/participant-questionnaire.jsx";
import ParticipantWaiting from "./questionaire/QuestionnaireWaiting.jsx";

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
                <Route path="/" element={<NewExperimentPage />} />

                <Route element={<Layout players={players} playerSlots={playerSlots} />}>
                    <Route path="/experiment/:experimentId/configure" element={<ConfigPage />} />
                    <Route path="/experiment/:experimentId/overview" element={<TrialOverview />} />
                </Route>
                <Route path="/participant/start" element={<QuestionnaireLanding />} />
                <Route path="/participant/demography" element={<ParticipantQuestionnaire />}/>
                <Route path="/participant/waiting" element={<ParticipantWaiting />} />
            </Routes>
        </BrowserRouter>
    )
}
