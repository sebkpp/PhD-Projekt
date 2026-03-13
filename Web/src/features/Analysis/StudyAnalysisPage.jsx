import React from "react";
import { useParams } from "react-router-dom";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import { useStudyPerformanceMetrics } from "@/features/Analysis/hooks/useStudyPerformanceMetrics.js";
import { useStudyUxMetrics } from "@/features/Analysis/hooks/useStudyUxMetrics.js";
import { useStudyEyeTrackingMetrics } from "@/features/Analysis/hooks/useStudyEyeTrackingMetrics.js";
import StudyPerformanceCharts from "@/features/Analysis/components/study/StudyPerformanceCharts.jsx";
import StudyQuestionnaireCharts from "@/features/Analysis/components/study/StudyQuestionnaireCharts.jsx";
import StudyEyeTrackingCharts from "@/features/Analysis/components/study/StudyEyeTrackingCharts.jsx";

const TABS = [
    { key: "performance", label: "Performance" },
    { key: "questionnaires", label: "Fragebögen" },
    { key: "eyetracking", label: "Eye-Tracking" },
];

export default function StudyAnalysisPage() {
    const { studyId } = useParams();

    const { data: studyPerformance, loading: perfLoading, error: perfError } =
        useStudyPerformanceMetrics(studyId);
    const { data: studyQuestionnaires, loading: uxLoading, error: uxError } =
        useStudyUxMetrics(studyId);
    const { data: studyEyeTracking, loading: etLoading, error: etError } =
        useStudyEyeTrackingMetrics(studyId);

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Studien-Analyse" },
    ];

    const loading = perfLoading || uxLoading || etLoading;
    const error = perfError || uxError || etError;

    if (loading) {
        return (
            <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
                <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
                <h1>Studien-Analyse</h1>
                <div className="flex items-center gap-3 mt-8 text-gray-300">
                    <svg
                        className="animate-spin h-6 w-6 text-blue-400"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8v8z"
                        />
                    </svg>
                    Lade Analysedaten…
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
                <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
                <h1>Studien-Analyse</h1>
                <div
                    className="mt-8 px-4 py-3 rounded text-red-300"
                    style={{ background: "#3b1a1a", border: "1px solid #7f1d1d" }}
                >
                    Fehler beim Laden der Daten: {error?.message || String(error)}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1>Studien-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="performance">
                <TabPanel tabKey="performance">
                    <StudyPerformanceCharts chartData={studyPerformance} />
                </TabPanel>
                <TabPanel tabKey="questionnaires">
                    <StudyQuestionnaireCharts chartData={studyQuestionnaires} />
                </TabPanel>
                <TabPanel tabKey="eyetracking">
                    <StudyEyeTrackingCharts chartData={studyEyeTracking} />
                </TabPanel>
            </ExperimentAnalyseTabs>
        </div>
    );
}
