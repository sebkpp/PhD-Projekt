import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import ConfigPage from './features/configuration/ConfigPage.jsx'
import TrialOverview from "./features/overview/TrialOverview.jsx";
import ExperimentOverview from './features/experiment/ExperimentOverview.jsx'

import ParticipantLanding from './features/participant/landing/ParticipantLandingPage.jsx'
import ParticipantQuestionnairePage from './features/participant/demography/ParticipantQuestionnairePage.jsx'
import ParticipantWaiting from "./features/questionnaire/QuestionnaireWaiting.jsx";
import SimulatorController from './debug/SimulatorController.jsx'
import QuestionnaireRouter from './features/questionnaire/QuestionnaireRouter'
import QuestionnaireClosing from "./features/questionnaire/QuestionnaireCloseing.jsx";
import StudyOverview from "./features/study/StudyOverview.jsx";
import StudyConfigurationPage from "@/features/study/StudyConfigPage.jsx";
import ExperimentConfigPage from "@/features/experiment/ExperimentConfigPage.jsx";
import AnalysisPage from '@/features/Analysis/AnalysisPage.jsx'
import StudyAnalysisPage from '@/features/Analysis/StudyAnalysisPage.jsx'
import ExperimentAnalysisPage from '@/features/Analysis/ExperimentAnalysisPage.jsx'

export default function AppRouter() {
    const playerSlots = [
        { id: 1, label: 'Proband 1' },
        { id: 2, label: 'Proband 2' }
    ]

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<StudyOverview />} />
                    <Route path="/study/configure" element={<StudyConfigurationPage />} />
                    <Route path="/study/:studyId/experiments" element={<ExperimentOverview />} />
                    <Route path="/study/:studyId/configure" element={<StudyConfigurationPage />} />
                    <Route path="/study/:studyId/experiment/configure" element={<ExperimentConfigPage />} />
                    <Route path="/study/:studyId/experiment/:experimentId/questionnaireForm" element={<QuestionnaireRouter />} />
                    <Route path="/study/:studyId/experiment/:experimentId/questionnaireStart" element={<ParticipantLanding />} />
                    <Route path="/study/:studyId/experiment/:experimentId/questionnaire" element={<ParticipantWaiting />} />
                    <Route path="/study/:studyId/experiment/:experimentId/participantdemography" element={<ParticipantQuestionnairePage />} />
                    <Route element={<Layout playerSlots={playerSlots} />}>
                        <Route path="/study/:studyId/experiment/:experimentId/overview" element={<TrialOverview />} />
                    </Route>

                    <Route path="/analysis" element={<AnalysisPage />} />
                    <Route path="/study/:studyId/analysis" element={<StudyAnalysisPage />} />
                    <Route path="/study/:studyId/experiment/:experimentId/analysis" element={<ExperimentAnalysisPage />} />

                    <Route path="/participant/questionnaires" element={<QuestionnaireRouter />} />
                    <Route path="/questionnaire/closing" element={<QuestionnaireClosing />} />
                    <Route path="/experiment/:experimentId/configure" element={<ConfigPage />} />

                    <Route path="/simulator" element={<SimulatorController />} />
                </Routes>
            </BrowserRouter>
        </div>
    )
}
