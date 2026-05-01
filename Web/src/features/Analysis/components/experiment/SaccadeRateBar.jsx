import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";

export default function SaccadeRateBar({ saccadeData }) {
    if (!saccadeData?.by_trial || Object.keys(saccadeData.by_trial).length === 0) return null;

    const barData = Object.entries(saccadeData.by_trial).map(([id, m]) => ({
        name: `Trial ${m.trial_number ?? id}`,
        giver: m.saccade_rate_giver !== null ? parseFloat(m.saccade_rate_giver.toFixed(2)) : null,
        receiver: m.saccade_rate_receiver !== null ? parseFloat(m.saccade_rate_receiver.toFixed(2)) : null,
    }));

    return (
        <div>
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis
                        label={{ value: "Sakk./s", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip />
                    <Legend verticalAlign="bottom" />
                    <Bar dataKey="giver" name="Geber" fill="#8884d8" />
                    <Bar dataKey="receiver" name="Empfänger" fill="#82ca9d" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
