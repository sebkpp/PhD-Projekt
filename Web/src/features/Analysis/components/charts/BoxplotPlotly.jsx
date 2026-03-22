import React from "react";
import Plot from "react-plotly.js";

const COLORS = [
    "#8884d8", // blau-lila
    "#82ca9d", // grün
    "#ffc658", // gelb
    "#ff7300", // orange
    "#00bcd4", // cyan
    "#e91e63"  // pink
];

export default function BoxplotPlotly({ boxplotData, chartRef, buttonRef, onExport }) {
    if (!boxplotData || boxplotData.length === 0) return null;

    const traces = boxplotData.map((d, i) => ({
        y: d.y,
        type: "box",
        name: d.name,
        boxpoints: "outliers",
        marker: { color: COLORS[i % COLORS.length] },
        line: { color: "#fff", width: 2 },
        fillcolor: COLORS[i % COLORS.length] + "80", // Transparenz für dunkles Design
        boxmean: false,
        showlegend: false
    }));
    
    const legendTraces = boxplotData.map((d, i) => ({
        y: [null],
        type: "box",
        name: d.name,
        marker: { color: COLORS[i % COLORS.length] },
        line: { color: "rgba(0,0,0,0)", width: 0 },
        fillcolor: COLORS[i % COLORS.length] + "80",
        showlegend: true
    }));

    const allTraces = [...traces, ...legendTraces];

    const annotations = boxplotData.flatMap((d) => [
        {
            x: d.name, y: d.min, text: `Min: ${d.min}`,
            showarrow: false, font: { color: "#fff", size: 12 }, yshift: 10
        },
        {
            x: d.name, y: d.q1, text: `Q1: ${d.q1}`,
            showarrow: false, font: { color: "#fff", size: 12 }, yshift: 10
        },
        {
            x: d.name, y: d.median, text: `Median: ${d.median}`,
            showarrow: false, font: { color: "#fff", size: 14 }, yshift: -10
        },
        {
            x: d.name, y: d.q3, text: `Q3: ${d.q3}`,
            showarrow: false, font: { color: "#fff", size: 12 }, yshift: -10
        },
        {
            x: d.name, y: d.max, text: `Max: ${d.max}`,
            showarrow: false, font: { color: "#fff", size: 12 }, yshift: -10
        }
    ]);

    const minY = Math.min(...boxplotData.map(d => d.min));
    const maxY = Math.max(...boxplotData.map(d => d.max));

    const padding = (maxY - minY) * 0.1;
    const yRange = [Math.max(0, minY - padding), maxY + padding];


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
                marginBottom: "2rem"
            }}
        >
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "0.5rem"
            }}>
                <h3 className="mb-2 export-hide text-base font-medium" style={{ margin: 0 }}>
                    Boxplot pro Trial
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
                        cursor: "pointer"
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
                        tickfont: { color: "#fff", size: 14 }
                    },
                    yaxis: {
                        title: { text: "Dauer (s)", font: { color: "#fff", size: 16 } },
                        tickfont: { color: "#fff", size: 14 },
                        gridcolor: "#444",
                        range: yRange, // Wertebereich manuell setzen
                        automargin: true
                    },
                    margin: { t: 20, l: 60, r: 20, b: 40 },
                    annotations,
                    legend: {
                        bgcolor: "#23272f",
                        bordercolor: "#444",
                        borderwidth: 0,
                        font: { color: "#fff", size: 14 },
                        orientation: "h",
                        x: 0.5,
                        xanchor: "center",
                        y: -0.25 // weiter nach unten
                    },
                    dragmode: false, // Ziehen deaktivieren
                    hovermode: "closest"
                }}
                config={{
                    displayModeBar: false,
                    responsive: true,
                    modeBarButtonsToRemove: ["zoom2d", "pan2d", "select2d", "lasso2d", "autoScale2d", "resetScale2d"]
                }}
                style={{ width: "100%", height: "350px" }}
            />
        </div>
    );
}