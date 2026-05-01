import React from "react";
import Plot from "react-plotly.js";
import { Table } from "antd";

const CONDITION_COLORS = {
    inner_hand: "#4e9af1",
    outer_hand: "#f5a623",
};

function formatPValue(p) {
    if (p === null || p === undefined) return "–";
    if (p < 0.001) return "< 0.001";
    return `${p.toFixed(3)}`;
}

function formatMeanStd(mean, std) {
    if (mean === null || mean === undefined) return "–";
    const m = typeof mean === "number" ? mean.toFixed(1) : mean;
    const s = typeof std === "number" ? std.toFixed(1) : (std ?? "–");
    return `${m} ± ${s}`;
}

function getEffectSizeLabel(d) {
    if (d === null || d === undefined) return "";
    const abs = Math.abs(d);
    if (abs < 0.2) return "(negligible)";
    if (abs < 0.5) return "(small)";
    if (abs < 0.8) return "(medium)";
    return "(large)";
}

export default function StudyPerformanceCharts({ chartData }) {
    if (!chartData?.performance) {
        return <div className="mt-8 text-gray-400">Keine Performance-Daten verfügbar.</div>;
    }

    const { by_condition, inferential } = chartData.performance;
    const conditions = chartData.conditions || ["inner_hand", "outer_hand"];
    const nExperiments = chartData.n_experiments ?? "–";

    const phases = [
        { key: "phase1", label: "Phase 1", meanKey: "phase1_mean", stdKey: "phase1_std" },
        { key: "phase2", label: "Phase 2", meanKey: "phase2_mean", stdKey: "phase2_std" },
        { key: "phase3", label: "Phase 3", meanKey: "phase3_mean", stdKey: "phase3_std" },
        { key: "total", label: "Total", meanKey: "total_mean", stdKey: "total_std" },
    ];

    // Grouped bar chart traces
    const traces = conditions.map(cond => ({
        name: cond,
        x: phases.map(p => p.label),
        y: phases.map(p => by_condition?.[cond]?.[p.meanKey] ?? 0),
        error_y: {
            type: "data",
            array: phases.map(p => by_condition?.[cond]?.[p.stdKey] ?? 0),
            visible: true,
            color: "#aaa",
            thickness: 2,
            width: 4,
        },
        type: "bar",
        marker: { color: CONDITION_COLORS[cond] || "#8884d8" },
    }));

    // Inferential table
    const tableData = phases.map(p => {
        const inf = inferential?.[p.key];
        const innerStats = by_condition?.["inner_hand"];
        const outerStats = by_condition?.["outer_hand"];
        return {
            key: p.key,
            metric: p.label,
            inner_hand: formatMeanStd(innerStats?.[p.meanKey], innerStats?.[p.stdKey]),
            outer_hand: formatMeanStd(outerStats?.[p.meanKey], outerStats?.[p.stdKey]),
            test: inf?.test ?? "–",
            statistic: inf?.statistic !== undefined ? inf.statistic.toFixed(3) : "–",
            p_value: formatPValue(inf?.p_value),
            cohens_d:
                inf?.effect_size_d !== undefined
                    ? `${inf.effect_size_d.toFixed(3)} ${getEffectSizeLabel(inf.effect_size_d)}`
                    : "–",
            significant: inf?.significant,
        };
    });

    const tableColumns = [
        { title: "Metrik", dataIndex: "metric", key: "metric" },
        { title: "inner_hand Ø±SD", dataIndex: "inner_hand", key: "inner_hand" },
        { title: "outer_hand Ø±SD", dataIndex: "outer_hand", key: "outer_hand" },
        { title: "Test", dataIndex: "test", key: "test" },
        { title: "Statistik", dataIndex: "statistic", key: "statistic" },
        {
            title: "p-Wert",
            dataIndex: "p_value",
            key: "p_value",
            render: val => <span>{val}</span>,
        },
        { title: "Cohen's d", dataIndex: "cohens_d", key: "cohens_d" },
        {
            title: "Signifikant",
            dataIndex: "significant",
            key: "significant",
            render: sig =>
                sig ? (
                    <span style={{ color: "#4ade80", fontWeight: 600 }}>✓ (p&lt;0.05)</span>
                ) : (
                    <span style={{ color: "#9ca3af" }}>✗</span>
                ),
        },
    ];

    return (
        <div className="mt-8">
            <h2 className="mb-4 text-xl font-semibold">Performance-Vergleich (Studie)</h2>

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
                    Mittlere Dauer nach Phase und Bedingung
                </h3>
                <Plot
                    data={traces}
                    layout={{
                        barmode: "group",
                        paper_bgcolor: "rgba(0,0,0,0)",
                        plot_bgcolor: "#1f2937",
                        font: { color: "#fff" },
                        xaxis: {
                            title: { text: "Phase", font: { color: "#fff", size: 14 } },
                            tickfont: { color: "#fff", size: 13 },
                        },
                        yaxis: {
                            title: { text: "Mittlere Dauer (ms)", font: { color: "#fff", size: 14 } },
                            tickfont: { color: "#fff", size: 13 },
                            gridcolor: "#444",
                        },
                        legend: {
                            bgcolor: "rgba(0,0,0,0)",
                            bordercolor: "#444",
                            font: { color: "#fff", size: 13 },
                            orientation: "h",
                            x: 0.5,
                            xanchor: "center",
                            y: -0.25,
                        },
                        margin: { t: 20, l: 70, r: 20, b: 80 },
                        dragmode: false,
                        hovermode: "closest",
                    }}
                    config={{ displayModeBar: false, responsive: true }}
                    style={{ width: "100%", height: "380px" }}
                />
            </div>

            <h2 className="mt-8 mb-4 text-xl font-semibold">Inferenzstatistik</h2>
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
                    footer={() => (
                        <span className="text-gray-400 text-sm">
                            n = {nExperiments} Experimente
                        </span>
                    )}
                />
            </div>
        </div>
    );
}
