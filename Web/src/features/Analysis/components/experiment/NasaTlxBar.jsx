import React from "react";
import {
    ResponsiveContainer, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";

const SUBSCALES = [
    "mental_demand", "physical_demand", "temporal_demand",
    "performance", "effort", "frustration",
];
const LABELS = {
    mental_demand: "Geistig",
    physical_demand: "Körperlich",
    temporal_demand: "Zeitlich",
    performance: "Leistung",
    effort: "Anstrengung",
    frustration: "Frustration",
};
const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"];

export default function NasaTlxBar({ trialItemStats }) {
    if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
    const trials = Object.entries(trialItemStats)
        .filter(([, t]) => t.questionnaires?.["NASA-TLX"]?.items?.length > 0)
        .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0));
    if (trials.length === 0) return null;

    const barData = SUBSCALES.map(key => {
        const entry = { name: LABELS[key] };
        trials.forEach(([, t]) => {
            const item = t.questionnaires["NASA-TLX"].items.find(i => i.item_name === key);
            entry[`Trial ${t.trial_number}`] = item ? parseFloat(item.mean.toFixed(1)) : null;
        });
        return entry;
    });

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis
                    domain={[0, 100]}
                    label={{ value: "Score", angle: -90, position: "insideLeft" }}
                />
                <Tooltip />
                <Legend verticalAlign="bottom" />
                {trials.map(([, t], i) => (
                    <Bar
                        key={t.trial_number}
                        dataKey={`Trial ${t.trial_number}`}
                        fill={COLORS[i % COLORS.length]}
                    />
                ))}
            </BarChart>
        </ResponsiveContainer>
    );
}
