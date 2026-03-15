import React from "react";
import Plot from "react-plotly.js";

export default function PhaseHeatmapPlotly({ phasesData, chartRef, buttonRef, onExport }) {
    if (!phasesData?.by_trial || Object.keys(phasesData.by_trial).length === 0) return null;

    const trials = Object.entries(phasesData.by_trial).sort(
        ([, a], [, b]) => a.trial_number - b.trial_number
    );

    // Collect all AOI names across all trials and phases (JSON integer keys become strings)
    const allAois = [...new Set(
        trials.flatMap(([, t]) =>
            ["1", "2", "3"].flatMap(p => Object.keys(t.phases?.[p] ?? {}))
        )
    )].sort();

    const xLabels = ["Phase 1", "Phase 2", "Phase 3"];
    const plotHeight = Math.max(200, allAois.length * 40);

    const darkLayout = {
        paper_bgcolor: "#23272f",
        plot_bgcolor: "#23272f",
        font: { color: "#fff" },
        margin: { t: 40, l: 80, r: 20, b: 50 },
        dragmode: false,
    };

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
                AOI-Verteilung pro Phase
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
                const z = allAois.map(aoi =>
                    ["1", "2", "3"].map(p => trialData.phases?.[p]?.[aoi]?.percentage ?? 0)
                );

                return (
                    <div key={trialId} style={{ marginBottom: "1rem" }}>
                        <Plot
                            data={[{
                                type: "heatmap",
                                x: xLabels,
                                y: allAois,
                                z,
                                colorscale: "Blues",
                                zmin: 0,
                                zmax: 100,
                                showscale: i === trials.length - 1,
                            }]}
                            layout={{
                                ...darkLayout,
                                title: {
                                    text: `Trial ${trialData.trial_number}`,
                                    font: { color: "#fff", size: 14 },
                                },
                                xaxis: { title: "Phase", tickfont: { color: "#fff" } },
                                yaxis: { title: "AOI", tickfont: { color: "#fff" } },
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
