import React from "react";
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

const CONDITION_LABELS = {
    inner_hand: "inner_hand",
    outer_hand: "outer_hand",
};

export default function StudyEyeTrackingCharts({ chartData }) {
    if (!chartData?.by_condition) {
        return <div className="mt-8 text-gray-400">Keine Eye-Tracking-Daten verfügbar.</div>;
    }

    const conditions = Object.keys(chartData.by_condition);

    if (conditions.length === 0) {
        return <div className="mt-8 text-gray-400">Keine Bedingungen vorhanden.</div>;
    }

    // Collect all AOI names across conditions
    const aoiNamesSet = new Set();
    conditions.forEach(cond => {
        Object.keys(chartData.by_condition[cond]?.aoi_stats || {}).forEach(name =>
            aoiNamesSet.add(name)
        );
    });
    const aoiNames = Array.from(aoiNamesSet);

    // Get label for an AOI (use first condition that has it)
    function getAoiLabel(aoiName) {
        for (const cond of conditions) {
            const stat = chartData.by_condition[cond]?.aoi_stats?.[aoiName];
            if (stat?.label) return stat.label;
        }
        return aoiName;
    }

    // Side-by-side stacked bar: one trace per AOI, X = conditions
    const stackedTraces = aoiNames.map((aoiName, idx) => ({
        name: getAoiLabel(aoiName),
        x: conditions.map(c => CONDITION_LABELS[c] || c),
        y: conditions.map(cond => {
            const stat = chartData.by_condition[cond]?.aoi_stats?.[aoiName];
            return stat?.percentage ?? 0;
        }),
        type: "bar",
        marker: { color: AOI_COLORS[idx % AOI_COLORS.length] },
    }));

    // Table data: one row per AOI
    const tableData = aoiNames.map(aoiName => {
        const row = {
            key: aoiName,
            aoi: aoiName,
            label: getAoiLabel(aoiName),
        };
        conditions.forEach(cond => {
            const stat = chartData.by_condition[cond]?.aoi_stats?.[aoiName];
            row[`${cond}_pct`] = stat ? `${stat.percentage?.toFixed(1)}%` : "–";
            row[`${cond}_fixations`] = stat?.fixation_count ?? "–";
        });
        return row;
    });

    const tableColumns = [
        { title: "AOI", dataIndex: "aoi", key: "aoi" },
        { title: "Label", dataIndex: "label", key: "label" },
        ...conditions.flatMap(cond => [
            {
                title: `${cond} – %`,
                dataIndex: `${cond}_pct`,
                key: `${cond}_pct`,
            },
            {
                title: `${cond} – Fixierungen`,
                dataIndex: `${cond}_fixations`,
                key: `${cond}_fixations`,
            },
        ]),
    ];

    return (
        <div className="mt-8">
            <h2 className="mb-4 text-xl font-semibold">Eye-Tracking – Vergleich nach Bedingung</h2>

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
                    AOI-Anteile (%) nach Stimulus-Bedingung
                </h3>
                <Plot
                    data={stackedTraces}
                    layout={{
                        barmode: "stack",
                        paper_bgcolor: "rgba(0,0,0,0)",
                        plot_bgcolor: "#1f2937",
                        font: { color: "#fff" },
                        xaxis: {
                            title: { text: "Bedingung", font: { color: "#fff", size: 14 } },
                            tickfont: { color: "#fff", size: 13 },
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

            <h2 className="mt-8 mb-4 text-xl font-semibold">AOI-Statistiken nach Bedingung</h2>
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
