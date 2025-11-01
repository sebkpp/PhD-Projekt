import React, {useRef} from "react";
import {useChartExport} from "@/features/Analysis/hooks/useChartExport.js";
import {
    groupChartData
} from "@/features/Analysis/utils/questionnaireUtils.js";
import QuestionnaireChartGroup from "@/features/Analysis/components/experiment/QuestionnaireChartGroup.jsx";

function getRangeForQuestionnaire(name) {
    const lower = name.toLowerCase();
    if (lower.includes("nasa") || lower.includes("tlx")) return [0, 100];
    if (lower.includes("likert")) return [0, 5];
    // Standard: automatische Range
    return undefined;
}

export default function QuestionnaireCharts({ chartData }) {
    const chartRefs = useRef({});
    const buttonRefs = useRef({});
    const exportChart = useChartExport();

    const handleExport = (name, trial_id) => {
        const chartRef = chartRefs.current[`${name}_${trial_id}`];
        const buttonRef = buttonRefs.current[`${name}_${trial_id}`];
        exportChart(chartRef, buttonRef, `${name}_trial_${trial_id}.png`);
    };

    const grouped = groupChartData(chartData.trial_item_stats);

    return (
        <div>
            <h2 className="mt-8 mb-4 text-xl font-semibold">UX-Metriken</h2>
            {grouped.map(([name, trials]) => (
                <QuestionnaireChartGroup
                    key={name}
                    name={name}
                    trials={trials}
                    chartRefs={chartRefs}
                    buttonRefs={buttonRefs}
                    onExport={handleExport}
                    meanDiffs={chartData.mean_diffs}
                    participants={chartData.participants}
                    questionnaireRange={getRangeForQuestionnaire(name)}
                />
            ))}
        </div>
    );
}