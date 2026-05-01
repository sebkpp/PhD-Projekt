import React from "react";
import {
    ResponsiveContainer, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, Cell,
} from "recharts";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"];

function calcAttrakDiffSubscales(items) {
    const groups = { pq: [], hqs: [], hqi: [], att: [] };
    items.forEach(({ item_name, mean }) => {
        for (const key of Object.keys(groups)) {
            if (item_name.startsWith(key + "_")) { groups[key].push(mean); break; }
        }
    });
    const avg = arr => arr.length
        ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2))
        : null;
    return { pq: avg(groups.pq), hqs: avg(groups.hqs), hqi: avg(groups.hqi), att: avg(groups.att) };
}

export default function AttrakDiffPortfolio({ trialItemStats }) {
    if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
    const scatterData = Object.entries(trialItemStats)
        .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
        .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0))
        .map(([, t]) => {
            const { pq, att } = calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items);
            if (pq == null || att == null) return null;
            return { x: pq, y: att, label: `Trial ${t.trial_number}` };
        })
        .filter(Boolean);
    if (scatterData.length === 0) return null;

    return (
        <ResponsiveContainer width="100%" height={340}>
            <ScatterChart margin={{ top: 20, right: 20, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                    type="number"
                    dataKey="x"
                    domain={[1, 7]}
                    name="PQ"
                    label={{ value: "PQ (Pragmatische Qualität)", position: "insideBottom", offset: -5 }}
                />
                <YAxis
                    type="number"
                    dataKey="y"
                    domain={[1, 7]}
                    name="ATT"
                    label={{ value: "ATT (Attraktivität)", angle: -90, position: "insideLeft" }}
                />
                <ReferenceLine x={4} stroke="#555" strokeDasharray="4 4" />
                <ReferenceLine y={4} stroke="#555" strokeDasharray="4 4" />
                <Tooltip
                    content={({ payload }) =>
                        payload?.[0] ? (
                            <div style={{ background: "#23272f", border: "1px solid #444", padding: "6px 10px", borderRadius: 6, color: "#fff", fontSize: 13 }}>
                                {payload[0].payload.label}: PQ={payload[0].payload.x}, ATT={payload[0].payload.y}
                            </div>
                        ) : null
                    }
                />
                <Scatter data={scatterData}>
                    {scatterData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                </Scatter>
            </ScatterChart>
        </ResponsiveContainer>
    );
}
