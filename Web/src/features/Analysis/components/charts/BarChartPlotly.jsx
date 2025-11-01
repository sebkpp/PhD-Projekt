import Plot from "react-plotly.js";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00bcd4", "#e91e63"];

function getTicksForRange(range) {
    if (!range || range.length !== 2) return undefined;
    const [min, max] = range;
    const step = (max - min) / 4; // 5 Werte = 4 Intervalle
    return Array.from({ length: 5 }, (_, i) => Math.round((min + i * step) * 100) / 100);
}

export default function BarChartPlotly({ chartData, participantIds, name, range }) {
    if (!chartData || chartData.length === 0) return null;

    const traces = participantIds.map((pid, idx) => ({
        x: chartData.map(row => row.item),
        y: chartData.map(row => row[pid]),
        name: `Participant ${pid}`,
        type: "bar",
        marker: { color: COLORS[idx % COLORS.length] }
    }));

    return (
        <Plot
            data={traces}
            layout={{
                barmode: "group",
                bargap: 0.2,
                bargroupgap: 0.05,
                xaxis: {
                    tickfont: { color: "#fff", size: 14 },
                    tickangle: -45
                },
                yaxis: {
                    tickfont: { color: "#fff", size: 14 },
                    gridcolor: "#444",
                    tickvals: getTicksForRange(range),
                    range: range || (name.toLowerCase().includes("likert") ? [0, 5] : undefined)
                },
                legend: {
                    orientation: "h",
                    y: -0.5,
                    x: 0.5,
                    xanchor: "center",
                    font: { color: "#fff", size: 13 }
                },
                plot_bgcolor: "#23272f",
                paper_bgcolor: "#23272f",
                font: { color: "#fff" },
                margin: { t: 30, l: 30, r: 30, b: 60 },
                hovermode: "closest",
                dragmode: false
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%", height: 300 }}
        />
    );
}