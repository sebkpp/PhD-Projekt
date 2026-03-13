import React from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { useParams } from "react-router-dom";
import {useExperiment} from "@/features/Analysis/hooks/useExperiment.js";
import ExperimentDetails from "@/features/Analysis/components/experiment/ExperimentDetails.jsx";
import {useParticipantsForExperiment} from "@/features/overview/hooks/useParticipantsForExperiment.js";
import QuestionnaireCharts from "@/features/Analysis/components/experiment/QuestionnaireCharts.jsx";
import PerformanceCharts from "@/features/Analysis/components/experiment/PerformanceCharts.jsx";
import EyeTrackingCharts from "@/features/Analysis/components/experiment/EyeTrackingCharts.jsx";
import ComparisonCharts from "@/features/Analysis/components/experiment/ComparisonCharts.jsx";
import {useHandovers} from "@/features/Analysis/hooks/useHandovers.js";
import {computePerformanceMetrics} from "@/features/Analysis/services/performanceMetrics.js";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import {useUxMetrics} from "@/features/Analysis/hooks/useUxMetrics.js";
import {usePerformanceMetrics} from "@/features/Analysis/hooks/usePerformanceMetrics.js";
import {useEyeTrackingMetrics} from "@/features/Analysis/hooks/useEyeTrackingMetrics.js";

const TABS = [
    { key: "details", label: "Experiment Info und Details" },
    { key: "ux", label: "UX" },
    { key: "performance", label: "Performance" },
    { key: "eyetracking", label: "Eye-Tracking" },
    { key: "compare", label: "Vergleiche" }
];

function computeMetricsPerTrial(handovers) {
    const grouped = {};
    handovers.forEach(h => {
        grouped[h.trial_id] = grouped[h.trial_id] || [];
        grouped[h.trial_id].push(h);
    });

    const metricsPerTrial = Object.entries(grouped).map(([trialId, trialHandovers]) => ({
        trialId,
        metrics: computePerformanceMetrics(trialHandovers)
    }));

    return metricsPerTrial;
}

export default function ExperimentAnalysisPage() {
    const { studyId, experimentId } = useParams();

    const { experiment, loading, error} =  useExperiment(experimentId);
    const { participants, loading : participant_loading,  error: participant_error} = useParticipantsForExperiment(experimentId);
    const { handovers, loading: handoversLoading, error: handoversError } = useHandovers(experimentId);
    const { data: uxMetrics, loading: uxLoading, error: uxError } = useUxMetrics(experimentId);
    const { data: performanceMetrics, loading: performanceLoading, error: performanceError } = usePerformanceMetrics(experimentId);
    const { data: eyeTrackingData, loading: eyeTrackingLoading, error: eyeTrackingError } = useEyeTrackingMetrics(experimentId);

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Experiment-Analyse" }
    ];

    if (loading || participant_loading || handoversLoading || uxLoading || performanceLoading || eyeTrackingLoading) {
        return <div>Lädt...</div>;
    }

    const metricsPerTrial = computeMetricsPerTrial(handovers);

    const experimentDetails = {
        study_id: experiment.study_id,
        experiment_id: experiment.experiment_id,
        researcher: experiment.researcher,
        description: experiment.description,
        created_at: experiment.created_at,
        started_at: experiment.started_at,
        completed_at: experiment.completed_at}

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1>Experiment-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="details">
                <TabPanel tabKey="details">
                    <ExperimentDetails experimentDetails={experimentDetails} />
                </TabPanel>
                <TabPanel tabKey="ux">
                    <QuestionnaireCharts chartData={uxMetrics} />
                </TabPanel>
                <TabPanel tabKey="performance">
                    <PerformanceCharts chartData={performanceMetrics} />
                </TabPanel>
                <TabPanel tabKey="eyetracking">
                    <EyeTrackingCharts chartData={eyeTrackingData} />
                </TabPanel>
                <TabPanel tabKey="compare">
                    <ComparisonCharts uxMetrics={uxMetrics} performanceMetrics={performanceMetrics} />
                </TabPanel>
            </ExperimentAnalyseTabs>
        </div>
    );
}