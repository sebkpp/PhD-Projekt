import React, { useRef } from "react";
import Plot from "react-plotly.js";
import { Table } from "antd";

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

export default function EyeTrackingCharts({ chartData }) {
    const chartRef = useRef(null);

    if (!chartData?.by_trial) {
        return (
            <div className="mt-8 text-gray-400">
                Keine Eye-Tracking-Daten verfügbar.
            </div>
        );
    }

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

    // Collect all AOI names across all trials
    const aoiNamesSet = new Set();
    trials.forEach(([, trialData]) => {
        Object.keys(trialData.aoi_stats || {}).forEach(name => aoiNamesSet.add(name));
    });
    const aoiNames = Array.from(aoiNamesSet);

    // Build X-axis labels
    const xLabels = trials.map(([, trialData]) => {
        const conditionNames = (trialData.stimuli_conditions || [])
            .map(c => c.type || c.name)
            .join(", ");
        return `Trial ${trialData.trial_number}${conditionNames ? ` (${conditionNames})` : ""}`;
    });

    // Build one trace per AOI
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

    // Build comparison table data
    const tableData = aoiNames.map((aoiName, idx) => {
        const row = {
            key: aoiName,
            aoi: aoiName,
            label: trials[0]?.[1]?.aoi_stats?.[aoiName]?.label || aoiName,
        };
        trials.forEach(([, trialData], tIdx) => {
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
        <div className="mt-8">
            <h2 className="mb-4 text-xl font-semibold">Eye-Tracking – AOI-Verteilung pro Trial</h2>

            <div
                ref={chartRef}
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
        </div>
    );
}
