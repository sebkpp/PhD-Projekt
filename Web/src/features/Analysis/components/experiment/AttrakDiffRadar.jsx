import React from "react";
import {
    ResponsiveContainer, RadarChart, Radar,
    PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    Tooltip, Legend,
} from "recharts";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"];

const SUBSCALES_RADAR = [
    { key: "pq",  subject: "PQ (Pragmatik)" },
    { key: "hqs", subject: "HQS (Stimulation)" },
    { key: "hqi", subject: "HQI (Identität)" },
    { key: "att", subject: "ATT (Attraktivität)" },
];

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

export default function AttrakDiffRadar({ trialItemStats }) {
    if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
    const trials = Object.entries(trialItemStats)
        .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
        .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0));
    if (trials.length === 0) return null;

    const trialSubscales = trials.map(([, t]) => ({
        label: `Trial ${t.trial_number}`,
        subs: calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items),
    }));

    const radarData = SUBSCALES_RADAR.map(({ key, subject }) => {
        const entry = { subject };
        trialSubscales.forEach(({ label, subs }) => {
            entry[label] = subs[key];
        });
        return entry;
    });

    return (
        <ResponsiveContainer width="100%" height={340}>
            <RadarChart cx="50%" cy="50%" outerRadius={110} data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={30} domain={[1, 7]} />
                <Tooltip />
                <Legend verticalAlign="bottom" />
                {trialSubscales.map(({ label }, i) => (
                    <Radar
                        key={label}
                        name={label}
                        dataKey={label}
                        stroke={COLORS[i % COLORS.length]}
                        fill={COLORS[i % COLORS.length]}
                        fillOpacity={0.3}
                    />
                ))}
            </RadarChart>
        </ResponsiveContainer>
    );
}
