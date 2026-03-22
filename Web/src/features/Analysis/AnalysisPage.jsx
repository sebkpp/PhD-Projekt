import React, { useState } from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { useStudies } from "@/features/study/hooks/useStudies.js";
import { fetchStudyPerformance } from "@/features/Analysis/services/studyAnalysisService.js";
import CrossStudyChart from "@/features/Analysis/components/CrossStudyChart.jsx";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";

const breadcrumbItems = [
    { label: "Studienübersicht", to: "/" },
    { label: "Studien-Meta-Analyse" },
];

function aggregateStudyPerformance(studyId, studyName, performanceData) {
    const byCondition = performanceData?.performance?.by_condition;
    if (!byCondition) return null;

    const conditions = Object.values(byCondition);
    const nTotal = conditions.reduce((sum, c) => sum + (c.n ?? 0), 0);
    if (nTotal === 0) return null;

    // Weighted mean across all conditions
    const weightedMean = conditions.reduce((sum, c) => sum + (c.total_mean ?? 0) * (c.n ?? 0), 0) / nTotal;
    // Weighted std
    const weightedStd = Math.sqrt(
        conditions.reduce((sum, c) => sum + Math.pow(c.total_std ?? 0, 2) * (c.n ?? 0), 0) / nTotal
    );
    const margin = 1.96 * (weightedStd / Math.sqrt(nTotal));

    return {
        label: studyName,
        mean: parseFloat(weightedMean.toFixed(3)),
        ci_lower: parseFloat(Math.max(0, weightedMean - margin).toFixed(3)),
        ci_upper: parseFloat((weightedMean + margin).toFixed(3)),
        n: nTotal,
    };
}

export default function AnalysisPage() {
    const { studies, loading: studiesLoading, error: studiesError } = useStudies();
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [baselineMs, setBaselineMs] = useState(300);
    const [chartData, setChartData] = useState(null);
    const [comparing, setComparing] = useState(false);
    const [compareError, setCompareError] = useState(null);

    const activeStudies = (studies || []).filter(s => s.status !== "Entwurf");

    function toggleStudy(id) {
        setSelectedIds(prev => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    }

    async function handleCompare() {
        setComparing(true);
        setCompareError(null);
        setChartData(null);
        try {
            const results = await Promise.all(
                [...selectedIds].map(id =>
                    fetchStudyPerformance(id)
                        .then(data => ({ id, data }))
                        .catch(() => ({ id, data: null }))
                )
            );
            const conditions = {};
            const failedStudies = [];
            for (const { id, data } of results) {
                const study = activeStudies.find(s => s.study_id === id);
                const label = study?.config?.name || `Studie ${id}`;
                const agg = aggregateStudyPerformance(id, label, data);
                if (agg) {
                    conditions[agg.label] = { mean: agg.mean, ci_lower: agg.ci_lower, ci_upper: agg.ci_upper, n: agg.n };
                } else {
                    failedStudies.push(label);
                }
            }
            // Note: null values are NOT stored in conditions — CrossStudyChart accesses stats.mean directly
            // and would throw a TypeError if stats is null. Failed studies are tracked separately.
            setChartData({ conditions, baseline_ms: baselineMs, failedStudies });
        } catch (err) {
            setCompareError(err.message);
        } finally {
            setComparing(false);
        }
    }

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Studien-Meta-Analyse</h1>

            {/* Study selection panel */}
            <div className="bg-gray-800 rounded-xl p-4 mb-6">
                <h2 className="text-lg font-semibold mb-3">Studien auswählen</h2>
                {studiesLoading && <LoadingSpinner message="Studien laden..." />}
                {studiesError && <ErrorMessage error={studiesError} />}
                {!studiesLoading && activeStudies.length === 0 && (
                    <p className="text-gray-400">Keine abgeschlossenen oder aktiven Studien vorhanden.</p>
                )}
                <div className="flex flex-col gap-2">
                    {activeStudies.map(study => (
                        <label key={study.study_id} className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedIds.has(study.study_id)}
                                onChange={() => toggleStudy(study.study_id)}
                                className="w-4 h-4"
                            />
                            <span>{study.config?.name || `Studie ${study.study_id}`}</span>
                            <span className="text-xs text-gray-400">({study.status})</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Baseline input */}
            <div className="flex items-center gap-3 mb-6">
                <label className="text-sm text-gray-300">Baseline (ms):</label>
                <input
                    type="number"
                    value={baselineMs}
                    onChange={e => setBaselineMs(Number(e.target.value))}
                    className="w-24 px-2 py-1 rounded bg-gray-700 border border-gray-600 text-white text-sm"
                    min={0}
                />
            </div>

            <button
                onClick={handleCompare}
                disabled={selectedIds.size < 2 || comparing}
                className="px-6 py-2 rounded bg-blue-700 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-600 mb-6"
            >
                {comparing ? "Vergleiche..." : "Studien vergleichen"}
            </button>
            {selectedIds.size < 2 && (
                <p className="text-xs text-gray-500 mb-4">Mindestens 2 Studien auswählen</p>
            )}

            {compareError && <ErrorMessage error={compareError} />}

            {comparing && <LoadingSpinner message="Daten werden geladen..." />}

            {chartData && !comparing && (
                <div>
                    <DescriptiveOnlyWarning message="Deskriptiver Vergleich — kein inferenzieller Test (unterschiedliche Teilnehmer je Studie)" />
                    <div className="mt-4">
                        <CrossStudyChart data={chartData} metric="Transfer Duration (ms)" />
                    </div>
                </div>
            )}
        </div>
    );
}
