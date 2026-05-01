import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

export default function ErrorRateBar({ chartData }) {
    if (!chartData?.by_trial) return null;

    const barData = Object.entries(chartData.by_trial).map(([id, m]) => ({
        name: id,
        errorRate: parseFloat(((m.error_rate ?? 0) * 100).toFixed(1)),
        errorCount: m.error_count ?? 0,
        totalCount: m.total_count ?? 0,
    }));

    if (barData.length === 0) return null;

    return (
        <div>
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis
                        domain={[0, 100]}
                        label={{ value: "%", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip
                        formatter={(v, _n, p) => [
                            `${v}% (${p.payload.errorCount}/${p.payload.totalCount})`,
                            "Fehlerrate",
                        ]}
                    />
                    <Bar dataKey="errorRate" fill="#e91e63" name="Fehlerrate" />
                </BarChart>
            </ResponsiveContainer>
            {barData.length > 0 && barData.every(d => d.errorRate === 0) && (
                <p className="text-xs text-gray-500 mt-1">Keine Fehler in diesem Experiment.</p>
            )}
        </div>
    );
}
