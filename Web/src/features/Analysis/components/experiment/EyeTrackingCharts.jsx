import React, { useRef } from "react";
import Plot from "react-plotly.js";
import { Table } from "antd";
import { useChartExport } from "@/features/Analysis/hooks/useChartExport.js";
import PhaseHeatmapPlotly from "@/features/Analysis/components/charts/PhaseHeatmapPlotly.jsx";
import TransitionMatrixPlotly from "@/features/Analysis/components/charts/TransitionMatrixPlotly.jsx";
import PPIBar from "@/features/Analysis/components/experiment/PPIBar.jsx";
import SaccadeRateBar from "@/features/Analysis/components/experiment/SaccadeRateBar.jsx";

const AOI_COLORS = [
    "#8884d8",
    "#82ca9d",
    "#ffc658",
    "#ff7300",
    "#00bcd4",
    "#e91e63",
    "#a4de6c",
    "#d0ed57",
];

export default function EyeTrackingCharts({ chartData, phasesData, transitionsData, ppiData, saccadeData }) {
    const chartRefs = useRef({});
    const buttonRefs = useRef({});
    // useChartExport() returns an async function with internal try/catch:
    //   exportChart(chartDivRef, buttonRef, filename) → triggers PNG download
    // Errors are caught and logged inside the hook; UI state (classes, button visibility)
    // is always restored. The caller does NOT need to await — identical pattern to PerformanceCharts.jsx.
    const exportChart = useChartExport();

    const handleExport = (key, filename) => {
        exportChart(chartRefs.current[key], buttonRefs.current[key], filename);
    };

    // Local helper — keeps Guard 2 (trials.length === 0) inside the chartData scope
    // without IIFE semantics. `return` here returns from renderAoiSection, not the component.
    function renderAoiSection() {
        if (!chartData?.by_trial) return null;

        const trials = Object.entries(chartData.by_trial).sort(
            ([, a], [, b]) => a.trial_number - b.trial_number
        );

        if (trials.length === 0) {
            return (
                <div className="mt-8 text-gray-400">
                    Keine Trial-Daten vorhanden.
                </div>
            );
        }

        const aoiNamesSet = new Set();
        trials.forEach(([, trialData]) => {
            Object.keys(trialData.aoi_stats || {}).forEach(name => aoiNamesSet.add(name));
        });
        const aoiNames = Array.from(aoiNamesSet);

        const xLabels = trials.map(([, trialData]) => {
            const conditionNames = (trialData.stimuli_conditions || [])
                .map(c => c.type || c.name)
                .join(", ");
            return `Trial ${trialData.trial_number}${conditionNames ? ` (${conditionNames})` : ""}`;
        });

        const traces = aoiNames.map((aoiName, idx) => ({
            x: xLabels,
            y: trials.map(([, trialData]) => {
                const stat = trialData.aoi_stats?.[aoiName];
                return stat ? stat.percentage : 0;
            }),
            name: aoiNames.length > 0
                ? (trials[0][1].aoi_stats?.[aoiName]?.label || aoiName)
                : aoiName,
            type: "bar",
            marker: { color: AOI_COLORS[idx % AOI_COLORS.length] },
        }));

        const tableData = aoiNames.map((aoiName) => {
            const row = {
                key: aoiName,
                aoi: aoiName,
                label: trials[0]?.[1]?.aoi_stats?.[aoiName]?.label || aoiName,
            };
            trials.forEach(([, trialData]) => {
                const stat = trialData.aoi_stats?.[aoiName];
                const trialNum = trialData.trial_number;
                row[`trial_${trialNum}_duration`] = stat ? stat.total_duration_ms?.toFixed(0) : "–";
                row[`trial_${trialNum}_pct`] = stat ? stat.percentage?.toFixed(1) : "–";
            });
            return row;
        });

        const tableColumns = [
            { title: "AOI", dataIndex: "aoi", key: "aoi" },
            { title: "Label", dataIndex: "label", key: "label" },
            ...trials.flatMap(([, trialData]) => {
                const trialNum = trialData.trial_number;
                const conditionNames = (trialData.stimuli_conditions || [])
                    .map(c => c.type || c.name)
                    .join(", ");
                const colTitle = `Trial ${trialNum}${conditionNames ? ` (${conditionNames})` : ""}`;
                return [
                    {
                        title: `${colTitle} – Dauer (ms)`,
                        dataIndex: `trial_${trialNum}_duration`,
                        key: `trial_${trialNum}_duration`,
                    },
                    {
                        title: `${colTitle} – %`,
                        dataIndex: `trial_${trialNum}_pct`,
                        key: `trial_${trialNum}_pct`,
                    },
                ];
            }),
        ];

        return (
            <>
                <h2 className="mb-4 text-xl font-semibold">Eye-Tracking – AOI-Verteilung pro Trial</h2>
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
                        AOI-Anteil (%) pro Trial
                    </h3>
                    <Plot
                        data={traces}
                        layout={{
                            barmode: "stack",
                            paper_bgcolor: "rgba(0,0,0,0)",
                            plot_bgcolor: "#1f2937",
                            font: { color: "#fff" },
                            xaxis: {
                                title: { text: "Trial", font: { color: "#fff", size: 14 } },
                                tickfont: { color: "#fff", size: 13 },
                                tickangle: -20,
                            },
                            yaxis: {
                                title: { text: "Anteil (%)", font: { color: "#fff", size: 14 } },
                                tickfont: { color: "#fff", size: 13 },
                                gridcolor: "#444",
                                range: [0, 100],
                            },
                            legend: {
                                bgcolor: "rgba(0,0,0,0)",
                                bordercolor: "#444",
                                font: { color: "#fff", size: 13 },
                                orientation: "h",
                                x: 0.5,
                                xanchor: "center",
                                y: -0.3,
                            },
                            margin: { t: 20, l: 60, r: 20, b: 80 },
                            dragmode: false,
                            hovermode: "closest",
                        }}
                        config={{ displayModeBar: false, responsive: true }}
                        style={{ width: "100%", height: "380px" }}
                    />
                </div>

                <h2 className="mt-8 mb-4 text-xl font-semibold">AOI-Statistiken im Vergleich</h2>
                <div
                    style={{
                        border: "1px solid #444",
                        borderRadius: "12px",
                        background: "#23272f",
                        boxShadow: "0 2px 8px #0002",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                        overflowX: "auto",
                    }}
                >
                    <Table
                        dataSource={tableData}
                        columns={tableColumns}
                        pagination={false}
                        rowClassName={() => "custom-dark-row"}
                        style={{ background: "transparent", color: "#fff" }}
                        bordered
                        scroll={{ x: "max-content" }}
                    />
                </div>
            </>
        );
    }

    return (
        <div className="mt-8">
            {/* Existing AOI stacked-bar + table — rendered via helper to keep Guard 2 scoped */}
            {renderAoiSection()}

            {/* New charts — each has its own internal guard (returns null when data missing) */}
            {/* chartRef/buttonRef use arrow-function callback pattern — NOT direct ref assignment */}
            <PhaseHeatmapPlotly
                phasesData={phasesData}
                chartRef={el => { chartRefs.current["phaseHeatmap"] = el; }}
                buttonRef={el => { buttonRefs.current["phaseHeatmap"] = el; }}
                onExport={() => handleExport("phaseHeatmap", "phase_heatmap.png")}
            />
            <TransitionMatrixPlotly
                transitionsData={transitionsData}
                chartRef={el => { chartRefs.current["transitionMatrix"] = el; }}
                buttonRef={el => { buttonRefs.current["transitionMatrix"] = el; }}
                onExport={() => handleExport("transitionMatrix", "transition_matrix.png")}
            />
            <h2 className="mt-8 mb-4 text-xl font-semibold">PPI pro Trial</h2>
            <PPIBar ppiData={ppiData} />
            <h2 className="mt-8 mb-4 text-xl font-semibold">Sakkaden-Rate pro Trial</h2>
            <SaccadeRateBar saccadeData={saccadeData} />
        </div>
    );
}
