import React from "react";
import Plot from "react-plotly.js";

const darkLayout = {
    paper_bgcolor: "#23272f",
    plot_bgcolor: "#23272f",
    font: { color: "#fff" },
    margin: { t: 40, l: 80, r: 20, b: 80 },
    dragmode: false,
};

export default function TransitionMatrixPlotly({ transitionsData, chartRef, buttonRef, onExport }) {
    if (!transitionsData?.by_trial || Object.keys(transitionsData.by_trial).length === 0) return null;

    const trials = Object.entries(transitionsData.by_trial).sort(
        ([, a], [, b]) => a.trial_number - b.trial_number
    );

    // Collect all AOIs across all trials for unified axis labels
    const globalAois = [...new Set(
        trials.flatMap(([, t]) =>
            Object.keys(t.transitions ?? {}).flatMap(key => key.split("->"))
        )
    )].sort();

    // Compute global max for synchronized color scale
    const allValues = trials.flatMap(([, t]) => Object.values(t.transitions ?? {}));
    const globalZMax = allValues.reduce((m, v) => Math.max(m, v), 1);

    const buildZ = (transitions) =>
        globalAois.map(from =>
            globalAois.map(to => transitions[`${from}->${to}`] ?? 0)
        );

    const plotHeight = Math.max(250, globalAois.length * 60);

    return (
        <div
            ref={chartRef}
            style={{
                border: "1px solid #444",
                borderRadius: "12px",
                background: "#23272f",
                boxShadow: "0 2px 8px #0002",
                padding: "1.5rem",
                marginBottom: "2rem",
                minWidth: 0,
            }}
        >
            <h3 className="export-hide" style={{ color: "#fff", marginBottom: "0.5rem" }}>
                AOI-Übergangs-Matrix
            </h3>
            <button
                ref={buttonRef}
                onClick={onExport}
                style={{
                    background: "#222",
                    border: "1px solid #555",
                    color: "#fff",
                    borderRadius: "6px",
                    padding: "4px 12px",
                    cursor: "pointer",
                    marginBottom: "1rem",
                    fontSize: "12px",
                }}
            >
                ⬇️ PNG
            </button>

            {trials.map(([trialId, trialData], i) => {
                const z = buildZ(trialData.transitions ?? {});

                return (
                    <div key={trialId} style={{ marginBottom: "1rem" }}>
                        <Plot
                            data={[{
                                type: "heatmap",
                                x: globalAois,
                                y: globalAois,
                                z,
                                colorscale: "Oranges",
                                zmin: 0,
                                zmax: globalZMax,
                                showscale: i === trials.length - 1,
                            }]}
                            layout={{
                                ...darkLayout,
                                title: {
                                    text: `Trial ${trialData.trial_number}`,
                                    font: { color: "#fff", size: 14 },
                                },
                                xaxis: {
                                    title: "nach AOI",
                                    tickfont: { color: "#fff" },
                                    tickangle: -30,
                                },
                                yaxis: { title: "von AOI", tickfont: { color: "#fff" } },
                                height: plotHeight,
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: "100%" }}
                        />
                    </div>
                );
            })}
        </div>
    );
}
