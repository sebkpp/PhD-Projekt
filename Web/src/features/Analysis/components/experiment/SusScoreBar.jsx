import React from "react";
import {
    ResponsiveContainer, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";

function calcSusScore(items) {
    const odd = ["sus_01", "sus_03", "sus_05", "sus_07", "sus_09"];
    const even = ["sus_02", "sus_04", "sus_06", "sus_08", "sus_10"];
    const itemMap = Object.fromEntries(items.map(i => [i.item_name, i.mean]));
    const sumOdd = odd.reduce((s, k) => s + ((itemMap[k] ?? 0) - 1), 0);
    const sumEven = even.reduce((s, k) => s + (5 - (itemMap[k] ?? 0)), 0);
    return parseFloat(((sumOdd + sumEven) * 2.5).toFixed(1));
}

function susGrade(score) {
    if (score >= 85) return "A";
    if (score >= 77) return "B";
    if (score >= 65) return "C";
    if (score >= 52) return "D";
    return "F";
}

export default function SusScoreBar({ trialItemStats }) {
    if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
    const barData = Object.entries(trialItemStats)
        .filter(([, t]) => t.questionnaires?.["SUS"]?.items?.length > 0)
        .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0))
        .map(([, t]) => ({
            name: `Trial ${t.trial_number}`,
            score: calcSusScore(t.questionnaires["SUS"].items),
        }));
    if (barData.length === 0) return null;

    return (
        <ResponsiveContainer width="100%" height={280}>
            <BarChart data={barData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis
                    domain={[0, 100]}
                    label={{ value: "SUS-Score", angle: -90, position: "insideLeft" }}
                />
                <Tooltip formatter={(v) => [`${v} (${susGrade(v)})`, "SUS-Score"]} />
                <ReferenceLine
                    y={68}
                    stroke="#ffc658"
                    strokeDasharray="4 4"
                    label={{ value: "Akzeptabel (68)", fill: "#ffc658", fontSize: 11 }}
                />
                <ReferenceLine
                    y={80.3}
                    stroke="#82ca9d"
                    strokeDasharray="4 4"
                    label={{ value: "Gut (80.3)", fill: "#82ca9d", fontSize: 11 }}
                />
                <Bar dataKey="score" fill="#8884d8" />
            </BarChart>
        </ResponsiveContainer>
    );
}
