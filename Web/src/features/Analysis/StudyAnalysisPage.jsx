import React, { useState } from "react";
import { useParams } from "react-router-dom";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import { useStudyPerformanceMetrics } from "@/features/Analysis/hooks/useStudyPerformanceMetrics.js";
import { useStudyUxMetrics } from "@/features/Analysis/hooks/useStudyUxMetrics.js";
import { useStudyEyeTrackingMetrics } from "@/features/Analysis/hooks/useStudyEyeTrackingMetrics.js";
import StudyPerformanceCharts from "@/features/Analysis/components/study/StudyPerformanceCharts.jsx";
import StudyQuestionnaireCharts from "@/features/Analysis/components/study/StudyQuestionnaireCharts.jsx";
import StudyEyeTrackingCharts from "@/features/Analysis/components/study/StudyEyeTrackingCharts.jsx";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import InferentialResultBadge from "@/features/Analysis/components/shared/InferentialResultBadge.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";
import { downloadStudyCsv, downloadStudyXlsx } from "@/features/Analysis/services/inferentialAnalysisService.js";

const TABS = [
    { key: "performance", label: "Performance" },
    { key: "questionnaires", label: "Fragebögen" },
    { key: "eyetracking", label: "Eye-Tracking" },
    { key: "export", label: "Export" },
];

function InferenzPanel({ inferential, label }) {
    if (!inferential || Object.keys(inferential).length === 0) return null;
    const entries = Object.entries(inferential);
    const hasAny = entries.some(([, v]) => v !== null);
    if (!hasAny) {
        return (
            <DescriptiveOnlyWarning message="Zu wenig Daten für inferenzielle Tests (n < 3 pro Bedingung)." />
        );
    }
    return (
        <div className="mt-6">
            <h3 className="text-base font-semibold mb-3">{label || "Inferenzielle Analyse"}</h3>
            <div className="flex flex-col gap-3">
                {entries.map(([key, result]) => (
                    <div key={key} className="bg-gray-800 rounded-lg p-3">
                        <div className="text-sm text-gray-400 mb-1">{key}</div>
                        <InferentialResultBadge result={result} />
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function StudyAnalysisPage() {
    const { studyId } = useParams();
    const [loadedTabs, setLoadedTabs] = useState(new Set(["performance"]));
    const [downloading, setDownloading] = useState(false);
    const [downloadError, setDownloadError] = useState(null);

    const { data: studyPerformance, loading: perfLoading, error: perfError } =
        useStudyPerformanceMetrics(studyId, true);
    const { data: studyQuestionnaires, loading: uxLoading, error: uxError } =
        useStudyUxMetrics(studyId, loadedTabs.has("questionnaires"));
    const { data: studyEyeTracking, loading: etLoading, error: etError } =
        useStudyEyeTrackingMetrics(studyId, loadedTabs.has("eyetracking"));

    function handleTabChange(tabKey) {
        setLoadedTabs(prev => new Set([...prev, tabKey]));
    }

    async function handleDownload(type) {
        setDownloading(true);
        setDownloadError(null);
        try {
            if (type === "csv") await downloadStudyCsv(studyId);
            else await downloadStudyXlsx(studyId);
        } catch (err) {
            setDownloadError(err.message);
        } finally {
            setDownloading(false);
        }
    }

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Studien-Analyse" },
    ];

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Studien-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="performance" onTabChange={handleTabChange}>
                <TabPanel tabKey="performance">
                    {perfLoading && <LoadingSpinner message="Performance-Daten laden..." />}
                    {perfError && <ErrorMessage error={perfError} />}
                    {studyPerformance && (
                        <>
                            <StudyPerformanceCharts chartData={studyPerformance} />
                            <InferenzPanel
                                inferential={studyPerformance?.performance?.inferential}
                                label="Inferenzielle Analyse — Transfer-Dauer"
                            />
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="questionnaires">
                    {uxLoading && <LoadingSpinner message="Fragebogen-Daten laden..." />}
                    {uxError && <ErrorMessage error={uxError} />}
                    {studyQuestionnaires && (
                        <>
                            <StudyQuestionnaireCharts chartData={studyQuestionnaires} />
                            {studyQuestionnaires?.questionnaires &&
                                Object.entries(studyQuestionnaires.questionnaires).map(([qName, qData]) => (
                                    <InferenzPanel
                                        key={qName}
                                        inferential={qData?.inferential}
                                        label={`Inferenzielle Analyse — ${qName}`}
                                    />
                                ))
                            }
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="eyetracking">
                    {etLoading && <LoadingSpinner message="Eye-Tracking-Daten laden..." />}
                    {etError && <ErrorMessage error={etError} />}
                    {studyEyeTracking && (
                        <>
                            <StudyEyeTrackingCharts chartData={studyEyeTracking} />
                            <InferenzPanel
                                inferential={studyEyeTracking?.inferential}
                                label="Inferenzielle Analyse — AOI Dwell-Time"
                            />
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="export">
                    <div className="mt-4">
                        <h2 className="text-lg font-semibold mb-4">Daten exportieren</h2>
                        {downloadError && <ErrorMessage error={downloadError} />}
                        <div className="flex gap-4 flex-wrap">
                            <button
                                onClick={() => handleDownload("csv")}
                                disabled={downloading}
                                className="px-6 py-2 rounded bg-green-700 text-white disabled:opacity-40 hover:bg-green-600"
                            >
                                {downloading ? "Wird exportiert..." : "CSV herunterladen"}
                            </button>
                            <button
                                onClick={() => handleDownload("xlsx")}
                                disabled={downloading}
                                className="px-6 py-2 rounded bg-blue-700 text-white disabled:opacity-40 hover:bg-blue-600"
                            >
                                {downloading ? "Wird exportiert..." : "Excel herunterladen"}
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-3">
                            Exportiert alle Handover-Daten der Studie {studyId}.
                        </p>
                    </div>
                </TabPanel>
            </ExperimentAnalyseTabs>
        </div>
    );
}
