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
    return p.toFixed(3);
}

function formatMeanStd(mean, std) {
    if (mean === null || mean === undefined) return "–";
    const m = typeof mean === "number" ? mean.toFixed(2) : mean;
    const s = typeof std === "number" ? std.toFixed(2) : (std ?? "–");
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

function SingleQuestionnaireSection({ name, data, nParticipants }) {
    const { by_condition, inferential } = data;
    const conditions = Object.keys(by_condition || {});

    // Collect all item names from any condition
    const itemNamesSet = new Set();
    conditions.forEach(cond => {
        Object.keys(by_condition[cond] || {}).forEach(item => itemNamesSet.add(item));
    });
    const itemNames = Array.from(itemNamesSet);

    if (itemNames.length === 0) {
        return <p className="text-gray-400">Keine Items vorhanden.</p>;
    }

    // Grouped bar chart per condition
    const traces = conditions.map(cond => ({
        name: cond,
        x: itemNames,
        y: itemNames.map(item => by_condition[cond]?.[item]?.mean ?? 0),
        error_y: {
            type: "data",
            array: itemNames.map(item => by_condition[cond]?.[item]?.std ?? 0),
            visible: true,
            color: "#aaa",
            thickness: 2,
            width: 4,
        },
        type: "bar",
        marker: { color: CONDITION_COLORS[cond] || "#8884d8" },
    }));

    // Inferential table
    const tableData = itemNames.map(item => {
        const inf = inferential?.[item];
        return {
            key: item,
            item,
            inner_hand: formatMeanStd(
                by_condition?.["inner_hand"]?.[item]?.mean,
                by_condition?.["inner_hand"]?.[item]?.std
            ),
            outer_hand: formatMeanStd(
                by_condition?.["outer_hand"]?.[item]?.mean,
                by_condition?.["outer_hand"]?.[item]?.std
            ),
            test: inf?.test ?? "–",
            p_value: formatPValue(inf?.p_value),
            cohens_d:
                inf?.effect_size_d !== undefined
                    ? `${inf.effect_size_d.toFixed(3)} ${getEffectSizeLabel(inf.effect_size_d)}`
                    : "–",
            significant: inf?.significant,
        };
    });

    const tableColumns = [
        { title: "Item", dataIndex: "item", key: "item" },
        { title: "inner_hand Ø±SD", dataIndex: "inner_hand", key: "inner_hand" },
        { title: "outer_hand Ø±SD", dataIndex: "outer_hand", key: "outer_hand" },
        { title: "Test", dataIndex: "test", key: "test" },
        {
            title: "p-Wert",
            dataIndex: "p_value",
            key: "p_value",
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
        <div className="mb-10">
            <h3
                className="text-lg font-semibold mb-3"
                style={{ color: "#e2e8f0", borderBottom: "1px solid #444", paddingBottom: "0.5rem" }}
            >
                {name}
            </h3>

            <div
                style={{
                    border: "1px solid #444",
                    borderRadius: "12px",
                    background: "#23272f",
                    boxShadow: "0 2px 8px #0002",
                    padding: "1.5rem",
                    marginBottom: "1.5rem",
                }}
            >
                <Plot
                    data={traces}
                    layout={{
                        barmode: "group",
                        paper_bgcolor: "rgba(0,0,0,0)",
                        plot_bgcolor: "#1f2937",
                        font: { color: "#fff" },
                        xaxis: {
                            tickfont: { color: "#fff", size: 12 },
                            tickangle: -20,
                            automargin: true,
                        },
                        yaxis: {
                            title: { text: "Mittelwert", font: { color: "#fff", size: 13 } },
                            tickfont: { color: "#fff", size: 12 },
                            gridcolor: "#444",
                        },
                        legend: {
                            bgcolor: "rgba(0,0,0,0)",
                            font: { color: "#fff", size: 12 },
                            orientation: "h",
                            x: 0.5,
                            xanchor: "center",
                            y: -0.35,
                        },
                        margin: { t: 20, l: 60, r: 20, b: 100 },
                        dragmode: false,
                        hovermode: "closest",
                    }}
                    config={{ displayModeBar: false, responsive: true }}
                    style={{ width: "100%", height: "320px" }}
                />
            </div>

            <div
                style={{
                    border: "1px solid #444",
                    borderRadius: "12px",
                    background: "#23272f",
                    boxShadow: "0 2px 8px #0002",
                    padding: "1.5rem",
                    marginBottom: "1rem",
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
                            n = {nParticipants ?? "–"} Teilnehmer
                        </span>
                    )}
                />
            </div>
        </div>
    );
}

export default function StudyQuestionnaireCharts({ chartData }) {
    if (!chartData?.questionnaires) {
        return <div className="mt-8 text-gray-400">Keine Fragebogen-Daten verfügbar.</div>;
    }

    const nParticipants = chartData.n_participants ?? "–";
    const questionnaireEntries = Object.entries(chartData.questionnaires);

    if (questionnaireEntries.length === 0) {
        return <div className="mt-8 text-gray-400">Keine Fragebögen vorhanden.</div>;
    }

    return (
        <div className="mt-8">
            <h2 className="mb-6 text-xl font-semibold">Fragebogen-Analyse (Studie)</h2>
            {questionnaireEntries.map(([name, data]) => (
                <SingleQuestionnaireSection
                    key={name}
                    name={name}
                    data={data}
                    nParticipants={nParticipants}
                />
            ))}
        </div>
    );
}
