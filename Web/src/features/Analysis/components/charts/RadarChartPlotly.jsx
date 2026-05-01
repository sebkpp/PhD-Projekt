import Plot from "react-plotly.js";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00bcd4", "#e91e63"];

export default function RadarChartPlotly({ radarData, trialLabels, range }) {
    if (!radarData || radarData.length === 0) return null;

    const items = radarData.map(d => d.item);

    const allValues = radarData.flatMap(d =>
        trialLabels.map((_, idx) => d[`trial${idx + 1}`] ?? 0)
    );

    const min = Math.floor(Math.min(...allValues));
    const max = Math.ceil(Math.max(...allValues));
    const usedRange = range || [min, max];

    const traces = trialLabels.map((label, idx) => ({
        type: "scatterpolar",
        r: radarData.map(d => d[`trial${idx + 1}`] ?? 0),
        theta: items,
        fill: "toself",
        name: label,
        line: { color: COLORS[idx % COLORS.length] },
        fillcolor: COLORS[idx % COLORS.length] + "55",
        marker: { color: COLORS[idx % COLORS.length] }
    }));

    return (
        <Plot
            data={traces}
            layout={{
                polar: {
                    bgcolor: "#23272f",
                    radialaxis: {
                        visible: true,
                        color: "#fff",
                        gridcolor: "#444",
                        tickfont: { color: "#fff" },
                        range: usedRange,
                        dtick: Math.ceil((usedRange[1] - usedRange[0]) / 5)
                    },
                    angularaxis: {
                        color: "#fff",
                        tickfont: { color: "#fff" },
                    }
                },
                paper_bgcolor: "#23272f",
                plot_bgcolor: "#23272f",
                font: { color: "#fff" },
                legend: {
                    orientation: "v",
                    x: -0.25,
                    y: 0.5,
                    xanchor: "right",
                    yanchor: "middle",
                    font: { color: "#fff", size: 13 }
                },
                margin: { t: 30, l: 30, r: 30, b: 30 },
                hovermode: "closest",
                dragmode: false
            }}
            config={{
                displayModeBar: false,
                responsive: true
            }}
            style={{ width: "100%", height: 300 }}
        />
    );
}