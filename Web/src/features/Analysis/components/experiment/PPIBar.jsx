import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ReferenceLine,
    ResponsiveContainer,
} from "recharts";

export default function PPIBar({ ppiData }) {
    if (!ppiData?.by_trial || Object.keys(ppiData.by_trial).length === 0) return null;

    const barData = Object.entries(ppiData.by_trial).map(([id, m]) => ({
        name: `Trial ${m.trial_number ?? id}`,
        giver: m.ppi_giver !== null ? parseFloat(m.ppi_giver.toFixed(1)) : null,
        receiver: m.ppi_receiver !== null ? parseFloat(m.ppi_receiver.toFixed(1)) : null,
    }));

    return (
        <div>
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis
                        domain={[0, 100]}
                        label={{ value: "%", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip />
                    <Legend verticalAlign="bottom" />
                    <ReferenceLine
                        y={30}
                        stroke="#ffc658"
                        strokeDasharray="4 4"
                        label={{ value: "30% (auto-haptisch)", fill: "#ffc658", fontSize: 11 }}
                    />
                    <Bar dataKey="giver" name="Geber" fill="#8884d8" />
                    <Bar dataKey="receiver" name="Empfänger" fill="#82ca9d" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
