import React, {useRef} from "react";
import {useChartExport} from "@/features/Analysis/hooks/useChartExport.js";
import {
    groupChartData
} from "@/features/Analysis/utils/questionnaireUtils.js";
import QuestionnaireChartGroup from "@/features/Analysis/components/experiment/QuestionnaireChartGroup.jsx";
import NasaTlxBar from "@/features/Analysis/components/experiment/NasaTlxBar.jsx";
import SusScoreBar from "@/features/Analysis/components/experiment/SusScoreBar.jsx";
import AttrakDiffPortfolio from "@/features/Analysis/components/experiment/AttrakDiffPortfolio.jsx";
import AttrakDiffRadar from "@/features/Analysis/components/experiment/AttrakDiffRadar.jsx";

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

    const hasQuestionnaire = (name) =>
        Object.values(chartData.trial_item_stats ?? {})
            .some(t => t.questionnaires?.[name]?.items?.length > 0);

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
            {hasQuestionnaire("NASA-TLX") && (
                <>
                    <h2 className="mt-8 mb-4 text-xl font-semibold">NASA-TLX Subskalen</h2>
                    <NasaTlxBar trialItemStats={chartData.trial_item_stats} />
                </>
            )}
            {hasQuestionnaire("SUS") && (
                <>
                    <h2 className="mt-8 mb-4 text-xl font-semibold">SUS-Score pro Trial</h2>
                    <SusScoreBar trialItemStats={chartData.trial_item_stats} />
                </>
            )}
            {hasQuestionnaire("AttrakDiff2") && (
                <>
                    <h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Portfolio-Matrix</h2>
                    <AttrakDiffPortfolio trialItemStats={chartData.trial_item_stats} />
                    <h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Subskalen-Radar</h2>
                    <AttrakDiffRadar trialItemStats={chartData.trial_item_stats} />
                </>
            )}
        </div>
    );
}