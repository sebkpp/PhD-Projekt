import React from "react";
import Plot from "react-plotly.js";

const COLORS = [
    "#8884d8",
    "#82ca9d",
    "#ffc658",
    "#ff7300",
    "#00bcd4",
    "#e91e63"
];

export default function ViolinPlotPlotly({ boxplotData, chartRef, buttonRef, onExport }) {
    if (!boxplotData || boxplotData.length === 0) return null;

    // Only y and name are used by the violin trace — other fields (min/q1/median/q3/max)
    // are intentionally omitted to avoid accidental Plotly prop pollution.
    const traces = boxplotData.map((d, i) => ({
        y: d.y,
        type: "violin",
        name: d.name,
        box: { visible: true },
        meanline: { visible: true },
        points: "outliers",
        marker: { color: COLORS[i % COLORS.length] },
        line: { color: COLORS[i % COLORS.length] },
        fillcolor: COLORS[i % COLORS.length] + "80",
        showlegend: false,
    }));

    const legendTraces = boxplotData.map((d, i) => ({
        y: [null],
        type: "violin",
        name: d.name,
        marker: { color: COLORS[i % COLORS.length] },
        line: { color: "rgba(0,0,0,0)", width: 0 },
        fillcolor: COLORS[i % COLORS.length] + "80",
        showlegend: true,
    }));

    const allTraces = [...traces, ...legendTraces];

    return (
        <div
            ref={chartRef}
            style={{
                border: "1px solid #444",
                borderRadius: "12px",
                background: "#23272f",
                boxShadow: "0 2px 8px #0002",
                padding: "1.5rem",
                minWidth: 0,
                marginBottom: "2rem",
            }}
        >
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "0.5rem",
            }}>
                <h3 className="mb-2 export-hide text-base font-medium" style={{ margin: 0 }}>
                    Violinplot pro Trial
                </h3>
                <button
                    ref={buttonRef}
                    onClick={onExport}
                    style={{
                        background: "#222",
                        border: "1px solid #555",
                        borderRadius: "4px",
                        padding: "2px 8px",
                        fontSize: "0.8rem",
                        cursor: "pointer",
                    }}
                    title="Chart als PNG exportieren"
                >
                    ⬇️ PNG
                </button>
            </div>
            <Plot
                data={allTraces}
                layout={{
                    paper_bgcolor: "#23272f",
                    plot_bgcolor: "#23272f",
                    font: { color: "#fff" },
                    xaxis: {
                        title: { text: "Trial", font: { color: "#fff", size: 16 } },
                        tickfont: { color: "#fff", size: 14 },
                    },
                    yaxis: {
                        title: { text: "Dauer (s)", font: { color: "#fff", size: 16 } },
                        tickfont: { color: "#fff", size: 14 },
                        gridcolor: "#444",
                        automargin: true,
                    },
                    margin: { t: 20, l: 60, r: 20, b: 40 },
                    legend: {
                        bgcolor: "#23272f",
                        bordercolor: "#444",
                        borderwidth: 0,
                        font: { color: "#fff", size: 14 },
                        orientation: "h",
                        x: 0.5,
                        xanchor: "center",
                        y: -0.25,
                    },
                    dragmode: false,
                    hovermode: "closest",
                }}
                config={{
                    displayModeBar: false,
                    responsive: true,
                }}
                style={{ width: "100%", height: "350px" }}
            />
        </div>
    );
}
