import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    ReferenceLine,
    LabelList
} from "recharts";

export default function DifferenceChart({ diffs, scaleName }) {
    if (!diffs.length) return null;
    const trialA = diffs[0].trialA;
    const trialB = diffs[0].trialB;

    const round1 = (x) => (Number.isFinite(x) ? Math.round(x * 10) / 10 : x);


    return (
        <div style={{ marginTop: "1rem" }}>
            <h3>{scaleName} – Differenzen (Trial {trialB} – Trial {trialA})</h3>
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={diffs} margin={{ top: 10, right: 0, left: 0, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#3a3f47" />
                    <XAxis dataKey="item" interval={0} angle={-45} textAnchor="end" />
                    <YAxis />
                    <Tooltip />
                    <ReferenceLine y={0} stroke="#aaa" />
                    <Bar dataKey="diff" fill="#3b82f6">
                        <LabelList dataKey="diff" position="top" formatter={(v) => round1(v)} />
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}