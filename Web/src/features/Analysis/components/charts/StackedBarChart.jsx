import Plot from "react-plotly.js";

const COLORS = {
    phase1: "#8884d8", // blau-lila
    phase2: "#82ca9d", // grün
    phase3: "#ffc658"  // gelb
};

function getPlotlyData(trialPhases) {
    return [
        {
            x: trialPhases.map(d => d.trial),
            y: trialPhases.map(d => d.phase1),
            name: "Phase 1 Ø (s)",
            type: "bar",
            marker: { color: COLORS.phase1 }
        },
        {
            x: trialPhases.map(d => d.trial),
            y: trialPhases.map(d => d.phase2),
            name: "Phase 2 Ø (s)",
            type: "bar",
            marker: { color: COLORS.phase2 }
        },
        {
            x: trialPhases.map(d => d.trial),
            y: trialPhases.map(d => d.phase3),
            name: "Phase 3 Ø (s)",
            type: "bar",
            marker: { color: COLORS.phase3 }
        }
    ];
}

function getAnnotations(trialPhases) {
    return trialPhases.map((d, i) => ({
        x: d.trial,
        y: d.phase1 + d.phase2 + d.phase3,
        text: `Ø: ${d.total_mean}`,
        showarrow: false,
        yshift: -20,
        font: { color: "#fff", size: 12 }
    })).concat(
        trialPhases.map((d, i) => ({
            x: d.trial,
            y: d.phase1 + d.phase2 + d.phase3,
            text: `n=${d.n}`,
            showarrow: false,
            yshift: -35,
            font: { color: "#fff", size: 11 }
        }))
    );
}

export default function StackedBarChart({ trialPhases, chartRef, buttonRef, onExport }) {
    const data = getPlotlyData(trialPhases);

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
                    Gestapelte Phasen pro Trial
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
                data={data}
                layout={{
                    barmode: "stack",
                    bargap: 0.2,
                    bargroupgap: 0.05,
                    xaxis: {
                        title: { text: "Trial", font: { color: "#fff", size: 16 } },
                        tickfont: { color: "#fff", size: 14 }
                    },
                    yaxis: {
                        title: { text: "Dauer (s)", font: { color: "#fff", size: 16 } },
                        tickfont: { color: "#fff", size: 14 },
                        gridcolor: "#444"
                    },
                    legend: {
                        orientation: "h",
                        y: -0.2,
                        font: { color: "#fff", size: 13 }
                    },
                    annotations: getAnnotations(trialPhases),
                    plot_bgcolor: "#23272f",
                    paper_bgcolor: "#23272f",
                    font: { color: "#fff" }
                }}
                style={{ width: "100%", height: 350 }}
                config={{ displayModeBar: false }}
            />
        </div>
    );
}