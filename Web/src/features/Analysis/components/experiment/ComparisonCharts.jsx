import React from "react";
import Plot from "react-plotly.js";

const CONDITION_COLORS = {
    trial1: "#8884d8",
    trial2: "#82ca9d",
};

export default function ComparisonCharts({ uxMetrics, performanceMetrics }) {
    const hasPerformance = performanceMetrics?.by_trial &&
        Object.keys(performanceMetrics.by_trial).length > 0;

    const hasUx = uxMetrics?.mean_diffs &&
        Object.keys(uxMetrics.mean_diffs).length > 0;

    return (
        <div className="mt-8">
            <h2 className="mb-4 text-xl font-semibold">Vergleiche</h2>

            <div
                className="mb-4 px-4 py-2 rounded text-sm text-yellow-300"
                style={{
                    background: "#2d2a1a",
                    border: "1px solid #665500",
                    borderRadius: "8px",
                }}
            >
                N = 2 Participants per Experiment – no inferential tests at this level
            </div>

            {hasPerformance && (
                <div
                    style={{
                        border: "1px solid #444",
                        borderRadius: "12px",
                        background: "#23272f",
                        boxShadow: "0 2px 8px #0002",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                    }}
                >
                    <h3 className="mb-2 text-base font-medium text-white">
                        Performance-Vergleich pro Trial (Gesamtdauer)
                    </h3>
                    <PerformanceBoxplots performanceMetrics={performanceMetrics} />
                </div>
            )}

            {!hasPerformance && (
                <div
                    style={{
                        border: "1px solid #444",
                        borderRadius: "12px",
                        background: "#23272f",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                    }}
                >
                    <p className="text-gray-400">Keine Performance-Daten verfügbar.</p>
                </div>
            )}

            {hasUx && (
                <div
                    style={{
                        border: "1px solid #444",
                        borderRadius: "12px",
                        background: "#23272f",
                        boxShadow: "0 2px 8px #0002",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                    }}
                >
                    <h3 className="mb-2 text-base font-medium text-white">
                        Fragebogen – mittlere Unterschiede zwischen Trials
                    </h3>
                    <UxMeanDiffsChart meanDiffs={uxMetrics.mean_diffs} />
                </div>
            )}

            {!hasUx && (
                <div
                    style={{
                        border: "1px solid #444",
                        borderRadius: "12px",
                        background: "#23272f",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                    }}
                >
                    <p className="text-gray-400">Keine Fragebogen-Daten verfügbar.</p>
                </div>
            )}
        </div>
    );
}

function PerformanceBoxplots({ performanceMetrics }) {
    const trials = Object.entries(performanceMetrics.by_trial);

    const colors = [CONDITION_COLORS.trial1, CONDITION_COLORS.trial2];

    const traces = trials.map(([trialId, metrics], idx) => ({
        y: metrics.total_values || [],
        type: "box",
        name: `Trial ${trialId}`,
        boxpoints: "outliers",
        marker: { color: colors[idx % colors.length] },
        line: { color: "#fff", width: 2 },
        fillcolor: (colors[idx % colors.length]) + "80",
    }));

    if (traces.every(t => !t.y || t.y.length === 0)) {
        return <p className="text-gray-400">Keine Rohdaten für Boxplot vorhanden.</p>;
    }

    return (
        <Plot
            data={traces}
            layout={{
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "#1f2937",
                font: { color: "#fff" },
                xaxis: {
                    title: { text: "Trial", font: { color: "#fff", size: 14 } },
                    tickfont: { color: "#fff", size: 13 },
                },
                yaxis: {
                    title: { text: "Gesamtdauer (ms)", font: { color: "#fff", size: 14 } },
                    tickfont: { color: "#fff", size: 13 },
                    gridcolor: "#444",
                },
                legend: {
                    bgcolor: "rgba(0,0,0,0)",
                    font: { color: "#fff", size: 13 },
                    orientation: "h",
                    x: 0.5,
                    xanchor: "center",
                    y: -0.25,
                },
                margin: { t: 20, l: 60, r: 20, b: 60 },
                dragmode: false,
                hovermode: "closest",
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%", height: "320px" }}
        />
    );
}

function UxMeanDiffsChart({ meanDiffs }) {
    // meanDiffs shape: { questionnaireName: { itemName: diffValue, ... }, ... }
    const items = [];
    const diffs = [];

    Object.entries(meanDiffs).forEach(([questionnaire, itemMap]) => {
        if (typeof itemMap === "object" && itemMap !== null) {
            Object.entries(itemMap).forEach(([item, diff]) => {
                items.push(`${questionnaire} – ${item}`);
                diffs.push(typeof diff === "number" ? diff : 0);
            });
        }
    });

    if (items.length === 0) {
        return <p className="text-gray-400">Keine Differenz-Daten verfügbar.</p>;
    }

    const barColors = diffs.map(d => (d >= 0 ? "#82ca9d" : "#ff7300"));

    return (
        <Plot
            data={[
                {
                    x: items,
                    y: diffs,
                    type: "bar",
                    marker: { color: barColors },
                    name: "Mittlere Differenz (Trial 1 – Trial 2)",
                },
            ]}
            layout={{
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "#1f2937",
                font: { color: "#fff" },
                xaxis: {
                    tickfont: { color: "#fff", size: 11 },
                    tickangle: -30,
                    automargin: true,
                },
                yaxis: {
                    title: { text: "Differenz", font: { color: "#fff", size: 14 } },
                    tickfont: { color: "#fff", size: 13 },
                    gridcolor: "#444",
                },
                margin: { t: 20, l: 60, r: 20, b: 120 },
                dragmode: false,
                hovermode: "closest",
                showlegend: false,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%", height: "340px" }}
        />
    );
}
