import React, {useRef} from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LabelList,
} from "recharts";
import { Table } from "antd";
import BoxplotPlotly from "@/features/Analysis/components/charts/BoxplotPlotly.jsx";
import ViolinPlotPlotly from "@/features/Analysis/components/charts/ViolinPlotPlotly.jsx";
import ErrorRateBar from "@/features/Analysis/components/experiment/ErrorRateBar.jsx";
import StackedBarChart from "@/features/Analysis/components/charts/StackedBarChart.jsx";
import {useChartExport} from "@/features/Analysis/hooks/useChartExport.js";

const COLORS = {
    total: "#8884d8",
    phase1: "#82ca9d",
    phase2: "#ffc658",
    phase3: "#ff7300"
};


function getTableData(chartData) {
    if (!chartData?.by_trial) return [];
    return Object.entries(chartData.by_trial).map(([trialId, metrics]) => ({
        key: trialId,
        trial: trialId,
        ...metrics
    }));
}

export default function PerformanceCharts({ chartData }) {
    const chartRefs = useRef({});
    const buttonRefs = useRef({});
    const exportChart = useChartExport();

    if (!chartData?.by_trial) return null;

    const handleExport = (key, filename) => {
        exportChart(
            chartRefs.current[key],
            buttonRefs.current[key],
            filename
        );
    };

    const trialPhases = Object.entries(chartData.by_trial).map(([trialId, metrics]) => ({
        trial: trialId,
        phase1: metrics.phase1_mean,
        phase2: metrics.phase2_mean,
        phase3: metrics.phase3_mean,
        total_mean: metrics.total_mean, // Hinzugefügt!
        n: metrics.n // Anzahl der Elemente
    }));

    const boxplotData = Object.entries(chartData.by_trial).map(([trialId, m]) => ({
        name: trialId,
        y: m.total_values,
        min: m.total_min,
        q1: m.total_q1,
        median: m.total_median,
        q3: m.total_q3,
        max: m.total_max
    }));

    console.log(boxplotData)

    const tableData = getTableData(chartData);
    const columns = [
        { title: "Trial", dataIndex: "trial" },
        { title: "Phase 1 Ø", dataIndex: "phase1_mean" },
        { title: "Phase 2 Ø", dataIndex: "phase2_mean" },
        { title: "Phase 3 Ø", dataIndex: "phase3_mean" },
        { title: "Total Ø", dataIndex: "total_mean" },
        { title: "Median", dataIndex: "total_median" },
        { title: "Std", dataIndex: "total_std" },
        { title: "Varianz", dataIndex: "total_var" },
        { title: "Min", dataIndex: "total_min" },
        { title: "Max", dataIndex: "total_max" },
        { title: "Q1", dataIndex: "total_q1" },
        { title: "Q3", dataIndex: "total_q3" },
        { title: "IQR", dataIndex: "total_iqr" },
        { title: "Skew", dataIndex: "total_skew" },
        { title: "Kurtosis", dataIndex: "total_kurtosis" },
        { title: "n", dataIndex: "n" },
        { title: "Normalität p", dataIndex: "total_normality_p" }
    ];
    console.log(boxplotData)
    return (
        <div className="mt-8">
            <h2 className="mb-4">Gestapelte Phasen pro Trial</h2>
            {/*<ResponsiveContainer width="100%" height={350}>*/}
            {/*    <BarChart data={trialPhases} barCategoryGap="20%">*/}
            {/*        <XAxis dataKey="trial" label={{ value: "Trial", position: "insideBottom", offset: -5 }} />*/}
            {/*        <YAxis label={{ value: "Dauer (s)", angle: -90, position: "insideLeft" }} />*/}
            {/*        <Tooltip />*/}
            {/*        <Legend />*/}
            {/*        <Bar dataKey="phase1" stackId="a" fill={COLORS.phase1} name="Phase 1 Ø (s)">*/}
            {/*            <LabelList dataKey="phase1" position="insideTop" formatter={v => v ?? "–"} />*/}
            {/*        </Bar>*/}
            {/*        <Bar dataKey="phase2" stackId="a" fill={COLORS.phase2} name="Phase 2 Ø (s)">*/}
            {/*            <LabelList dataKey="phase2" position="insideTop" formatter={v => v ?? "–"} />*/}
            {/*        </Bar>*/}
            {/*        <Bar dataKey="phase3" stackId="a" fill={COLORS.phase3} name="Phase 3 Ø (s)">*/}
            {/*            <LabelList dataKey="phase3" position="insideTop" formatter={v => v ?? "–"} />*/}
            {/*            <LabelList dataKey="total_mean" position="top" formatter={v => v ?? "–"} />*/}
            {/*            <LabelList dataKey="n" position="insideTopRight" formatter={v => `n=${v ?? "–"}`} />*/}
            {/*        </Bar>*/}
            {/*    </BarChart>*/}
            {/*</ResponsiveContainer>*/}

            <StackedBarChart
                trialPhases={trialPhases}
                chartRef={el => chartRefs.current["stackedbar"] = el}
                buttonRef={el => buttonRefs.current["stackedbar"] = el}
                onExport={() => handleExport("stackedbar", "stackedbar.png")}
            />

            <BoxplotPlotly
                boxplotData={boxplotData}
                chartRef={el => chartRefs.current["boxplot"] = el}
                buttonRef={el => buttonRefs.current["boxplot"] = el}
                onExport={() => handleExport("boxplot", "boxplot.png")}
            />

            <ViolinPlotPlotly
                boxplotData={boxplotData}
                chartRef={el => chartRefs.current["violin"] = el}
                buttonRef={el => buttonRefs.current["violin"] = el}
                onExport={() => handleExport("violin", "violinplot.png")}
            />

            <h2 className="mt-8 mb-4">Statistische Kennzahlen pro Trial</h2>
            <div
                style={{
                    border: "1px solid #444",
                    borderRadius: "12px",
                    background: "#23272f",
                    boxShadow: "0 2px 8px #0002",
                    padding: "1.5rem",
                    minWidth: 0,
                    marginBottom: "2rem",
                    maxWidth: "100%",
                    overflowX: "auto"
                }}
            >
                <Table
                    dataSource={tableData}
                    columns={columns}
                    pagination={false}
                    rowClassName={() => "custom-dark-row"}
                    style={{
                        background: "transparent",
                        color: "#fff"
                    }}
                    bordered
                    scroll={{ x: "max-content" }}
                />
            </div>

            <h2 className="mt-8 mb-4">Fehlerrate pro Trial</h2>
            <ErrorRateBar chartData={chartData} />

        </div>
    )
}