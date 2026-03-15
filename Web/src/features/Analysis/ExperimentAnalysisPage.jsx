import React, { useState } from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { useParams } from "react-router-dom";
import { useExperiment } from "@/features/Analysis/hooks/useExperiment.js";
import ExperimentDetails from "@/features/Analysis/components/experiment/ExperimentDetails.jsx";
import { useParticipantsForExperiment } from "@/features/overview/hooks/useParticipantsForExperiment.js";
import QuestionnaireCharts from "@/features/Analysis/components/experiment/QuestionnaireCharts.jsx";
import PerformanceCharts from "@/features/Analysis/components/experiment/PerformanceCharts.jsx";
import EyeTrackingCharts from "@/features/Analysis/components/experiment/EyeTrackingCharts.jsx";
import ComparisonCharts from "@/features/Analysis/components/experiment/ComparisonCharts.jsx";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import { useUxMetrics } from "@/features/Analysis/hooks/useUxMetrics.js";
import { usePerformanceMetrics } from "@/features/Analysis/hooks/usePerformanceMetrics.js";
import { useEyeTrackingMetrics } from "@/features/Analysis/hooks/useEyeTrackingMetrics.js";
import { useEyeTrackingPhases } from "@/features/Analysis/hooks/useEyeTrackingPhases.js";
import { useEyeTrackingTransitions } from "@/features/Analysis/hooks/useEyeTrackingTransitions.js";
import { usePPI } from "@/features/Analysis/hooks/usePPI.js";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";
import PlaceholderChart from "@/features/Analysis/components/shared/PlaceholderChart.jsx";

const TABS = [
    { key: "details", label: "Experiment Info" },
    { key: "performance", label: "Performance" },
    { key: "eyetracking", label: "Eye-Tracking" },
    { key: "ux", label: "Fragebögen / UX" },
    { key: "compare", label: "Vergleiche" },
];

const DESCRIPTIVE_WARNING =
    "Deskriptive Analyse eines Messdurchgangs. Inferenzielle Auswertung über alle Experimente → Studien-Analyse.";

export default function ExperimentAnalysisPage() {
    const { studyId, experimentId } = useParams();
    const [loadedTabs, setLoadedTabs] = useState(new Set(["details"]));

    const { experiment, loading: expLoading, error: expError } = useExperiment(experimentId);
    const { participants, loading: _partLoading } = useParticipantsForExperiment(experimentId);

    const { data: uxMetrics, loading: uxLoading, error: uxError } =
        useUxMetrics(experimentId, loadedTabs.has("ux") || loadedTabs.has("compare"));
    const { data: performanceMetrics, loading: perfLoading, error: perfError } =
        usePerformanceMetrics(experimentId, loadedTabs.has("performance") || loadedTabs.has("compare"));
    const { data: eyeTrackingData, loading: etLoading, error: etError } =
        useEyeTrackingMetrics(experimentId, loadedTabs.has("eyetracking"));
    const { data: _etPhasesData, loading: phasesLoading, error: phasesError } =
        useEyeTrackingPhases(experimentId, loadedTabs.has("eyetracking"));
    // etTransitionsData prefixed with _ — data is fetched now but rendered in Session B (TransitionSankey)
    const { data: _etTransitionsData, loading: transLoading, error: transError } =
        useEyeTrackingTransitions(experimentId, loadedTabs.has("eyetracking"));
    const { data: ppiData, loading: ppiLoading, error: ppiError } =
        usePPI(experimentId, loadedTabs.has("eyetracking"));

    function handleTabChange(tabKey) {
        if (tabKey === "compare") {
            setLoadedTabs(prev => new Set([...prev, tabKey, "performance", "ux"]));
        } else {
            setLoadedTabs(prev => new Set([...prev, tabKey]));
        }
    }

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Experiment-Analyse" },
    ];

    const experimentDetails = experiment ? {
        study_id: experiment.study_id,
        experiment_id: experiment.experiment_id,
        researcher: experiment.researcher,
        description: experiment.description,
        created_at: experiment.created_at,
        started_at: experiment.started_at,
        completed_at: experiment.completed_at,
    } : null;

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Experiment-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="details" onTabChange={handleTabChange}>

                {/* === DETAILS === */}
                <TabPanel tabKey="details">
                    {expLoading && <LoadingSpinner message="Experiment laden..." />}
                    {expError && <ErrorMessage error={expError} />}
                    {experimentDetails && (
                        <ExperimentDetails experimentDetails={experimentDetails} participants={participants} />
                    )}
                </TabPanel>

                {/* === PERFORMANCE === */}
                <TabPanel tabKey="performance">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {perfLoading && <LoadingSpinner message="Performance-Daten laden..." />}
                    {perfError && <ErrorMessage error={perfError} />}
                    {performanceMetrics && <PerformanceCharts chartData={performanceMetrics} />}
                    {/* SESSION B: PerformanceViolin */}
                    <PlaceholderChart label="Violinplot pro Bedingung (kommt in Session B)" />
                    {/* SESSION B: ErrorRateBar */}
                    <PlaceholderChart label="Fehlerrate pro Bedingung (kommt in Session B)" />
                </TabPanel>

                {/* === EYE-TRACKING === */}
                <TabPanel tabKey="eyetracking">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {etLoading && <LoadingSpinner message="Eye-Tracking-Daten laden..." />}
                    {etError && <ErrorMessage error={etError} />}
                    {eyeTrackingData && <EyeTrackingCharts chartData={eyeTrackingData} />}

                    {/* Phase + Transition data loading states */}
                    {(phasesLoading || transLoading) && <LoadingSpinner message="Phasen & Transitionen laden..." />}
                    {phasesError && <ErrorMessage error={phasesError} />}
                    {transError && <ErrorMessage error={transError} />}
                    {/* etTransitionsData is fetched here and will be consumed by Session B's TransitionSankey */}

                    {/* PPI display */}
                    {ppiLoading && <LoadingSpinner message="PPI berechnen..." />}
                    {ppiError && <ErrorMessage error={ppiError} />}
                    {ppiData && ppiData.by_trial && (
                        <div className="mt-4 bg-gray-800 rounded-xl p-4">
                            <h3 className="text-sm font-semibold mb-2">Proaktiver Planungsindex (PPI)</h3>
                            <p className="text-xs text-gray-400 mb-2">
                                Anteil der Geber-Blickzeit auf den Aufgabenbereich (environment) in Phase 3.
                                Hoher PPI (&gt;30%) = automatisch-haptische Übergabe.
                            </p>
                            <div className="flex flex-wrap gap-3">
                                {Object.values(ppiData.by_trial).map(trial => (
                                    <div key={trial.trial_number} className="text-xs bg-gray-700 rounded px-3 py-2">
                                        <div className="font-medium">Trial {trial.trial_number}</div>
                                        <div>Geber: {trial.ppi_giver !== null ? `${trial.ppi_giver.toFixed(1)}%` : "–"}</div>
                                        <div>Empfänger: {trial.ppi_receiver !== null ? `${trial.ppi_receiver.toFixed(1)}%` : "–"}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="AOI × Phasen-Heatmap (kommt in Session B)" />
                    <PlaceholderChart label="Blickpfad-Sankey (kommt in Session B)" />
                    <PlaceholderChart label="Sakkaden-Rate pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="Gaze-Timeline (kommt in Session B)" />
                    <PlaceholderChart label="PPI-Balkendiagramm pro Bedingung (kommt in Session B)" />
                </TabPanel>

                {/* === UX / QUESTIONNAIRES === */}
                <TabPanel tabKey="ux">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {uxLoading && <LoadingSpinner message="Fragebogen-Daten laden..." />}
                    {uxError && <ErrorMessage error={uxError} />}
                    {uxMetrics && <QuestionnaireCharts chartData={uxMetrics} />}
                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="NASA-TLX Subskalen pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="SUS-Score pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="AttrakDiff2 Portfolio-Matrix (kommt in Session B)" />
                    <PlaceholderChart label="AttrakDiff2 Subskalen-Radar (kommt in Session B)" />
                </TabPanel>

                {/* === COMPARE === */}
                <TabPanel tabKey="compare">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {(perfLoading || uxLoading) && <LoadingSpinner message="Vergleichsdaten laden..." />}
                    {(perfError || uxError) && <ErrorMessage error={perfError || uxError} />}
                    {performanceMetrics && uxMetrics && (
                        <ComparisonCharts uxMetrics={uxMetrics} performanceMetrics={performanceMetrics} />
                    )}
                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="Korrelationsmatrix (kommt in Session B)" />
                </TabPanel>

            </ExperimentAnalyseTabs>
        </div>
    );
}
