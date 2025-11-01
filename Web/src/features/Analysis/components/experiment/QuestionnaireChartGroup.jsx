import React from "react";
import {
    LabelList,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer
} from "recharts";
import { getMaxValue} from "@/features/Analysis/utils/questionnaireUtils.js";
import RadarChartPlotly from "@/features/Analysis/components/charts/RadarChartPlotly.jsx";
import BarChartPlotly from "@/features/Analysis/components/charts/BarChartPlotly.jsx";

function getDiffDataFromBackend(meanDiffs, questionnaireName) {
    const diffsArr = meanDiffs[questionnaireName] || [];
    if (!Array.isArray(diffsArr) || diffsArr.length === 0) {
        return [];
    }
    return [...diffsArr].sort((a, b) => a.questionnaire_item_id - b.questionnaire_item_id)
        .map(({ item_name, value }) => ({
            item: item_name,
            diff: Math.round(value * 10) / 10
        }));
}

function prepareParticipantChartData(participantsObj, trialId, questionnaireName) {
    if (!participantsObj) return [];
    const participantIds = Object.keys(participantsObj);

    const itemsSet = new Set();
    participantIds.forEach(pid => {
        const responsesArr = participantsObj[pid]?.[trialId]?.[questionnaireName]?.responses;
        if (Array.isArray(responsesArr)) {
            responsesArr.forEach(r => itemsSet.add(r.item_name));
        }
    });
    const items = Array.from(itemsSet);

    return items.map(item => {
        const row = { item };
        participantIds.forEach(pid => {
            const responsesArr = participantsObj[pid]?.[trialId]?.[questionnaireName]?.responses;
            const responseObj = Array.isArray(responsesArr)
                ? responsesArr.find(r => r.item_name === item)
                : undefined;
            row[pid] = responseObj ? responseObj.response_value : null;
        });
        return row;
    });
}

export default function QuestionnaireChartGroup({name, trials = [], chartRefs, buttonRefs, onExport, meanDiffs, participants, questionnaireRange}) {
    const diffData = getDiffDataFromBackend(meanDiffs, name);
    const diffs = diffData.map(d => d.diff);
    const range = Math.max(...diffs) - Math.min(...diffs) || 1;
    const minDiff = Math.floor(Math.min(...diffs) - range * 0.2);
    const maxDiff = Math.ceil(Math.max(...diffs) + range * 0.2);
    const radarData = [];
    if (trials.length > 0) {
        const items = trials[0][1]?.map(row => row.item) || [];
        items.forEach(item => {
            const entry = {item};
            trials.forEach(([trial_id, data], idx) => {
                const mean = data.find(row => row.item === item)?.mean ?? 0;
                entry[`trial${idx + 1}`] = mean;
            });
            radarData.push(entry);
        });
    }

    return (
        <div
            style={{
                flex: 1,
                border: "1px solid #444",
                borderRadius: "12px",
                background: "#23272f",
                boxShadow: "0 2px 8px #0002",
                padding: "1.5rem",
                minWidth: 0,
                marginBottom: "2rem"
            }}
        >
            <h2 className="mb-4 text-lg font-semibold">{name}</h2>
            <div style={{display: "flex", gap: "2rem"}}>
                {trials.map(([trial_id, data]) => {
                    // Teilnehmer-IDs aus den Daten extrahieren
                    const chartData = prepareParticipantChartData(participants, trial_id, name);
                    const participantIds = Object.keys(chartData[0]).filter(k => k !== "item");                    // Mittelwerte/Std für die Tabelle
                    const stats = data.map(row => ({
                        item: row.item,
                        mean: row.mean,
                        std: row.std
                    }));
                    return (
                        <div
                            key={trial_id}
                            className="mb-8"
                            ref={el => chartRefs.current[`${name}_${trial_id}`] = el}
                            style={{ position: "relative", flex: 1 }}
                        >
                            <div style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                marginBottom: "0.5rem"
                            }}>
                                <h3 className="mb-2 export-hide text-base font-medium"
                                    style={{ margin: 0 }}>Trial {trial_id}</h3>
                                <button
                                    ref={el => buttonRefs.current[`${name}_${trial_id}`] = el}
                                    onClick={() => onExport(name, trial_id)}
                                    style={{
                                        background: "#222",
                                        border: "1px solid #555",
                                        borderRadius: "4px",
                                        padding: "2px 8px",
                                        fontSize: "0.8rem",
                                        cursor: "pointer"
                                    }}
                                    title="Chart als PNG exportieren"
                                >
                                    ⬇️ PNG
                                </button>
                            </div>
                            {/*<ResponsiveContainer width="100%" height={300}>*/}
                            {/*    <BarChart data={chartData}*/}
                            {/*              margin={{ top: 20, right: 0, left: 0, bottom: 50 }}*/}
                            {/*    >*/}
                            {/*        <XAxis dataKey="item" interval={0} angle={-45} textAnchor="end" />*/}
                            {/*        <YAxis domain={[0, getMaxValue(name)]}*/}
                            {/*               ticks={name.toLowerCase().includes("likert") ? [0, 1, 2, 3, 4, 5] : undefined} />*/}
                            {/*        <Tooltip*/}
                            {/*            contentStyle={{*/}
                            {/*                background: "#23272f",*/}
                            {/*                border: "1px solid #444",*/}
                            {/*                color: "#fff",*/}
                            {/*                borderRadius: "8px",*/}
                            {/*                boxShadow: "0 2px 8px #0004"*/}
                            {/*            }}*/}
                            {/*            itemStyle={{*/}
                            {/*                color: "#fff"*/}
                            {/*            }}*/}
                            {/*        />*/}
                            {/*        {participantIds.map((pid, idx) => (*/}
                            {/*            <Bar key={pid} dataKey={pid} fill={idx === 0 ? "#8884d8" : "#82ca9d"}*/}
                            {/*                 name={`Participant ${pid}`}>*/}
                            {/*                <LabelList dataKey={pid} position="top" />*/}
                            {/*            </Bar>*/}
                            {/*        ))}*/}
                            {/*    </BarChart>*/}
                            {/*</ResponsiveContainer>*/}
                            <BarChartPlotly
                                chartData={chartData}
                                participantIds={participantIds}
                                name={name}
                                range={questionnaireRange}
                            />
                            {/*<div className="chart-legend" style={{ textAlign: "center", marginTop: "1rem" }}>*/}
                            {/*    {participantIds.map((pid, idx) => (*/}
                            {/*        <span key={pid}*/}
                            {/*              style={{ marginRight: "1.5rem", color: idx === 0 ? "#8884d8" : "#82ca9d" }}>*/}
                            {/*            &#9632; Participant {pid}*/}
                            {/*        </span>*/}
                            {/*    ))}*/}
                            {/*</div>*/}
                            <div className="export-hide" style={{ marginTop: "0.5rem", fontSize: "0.95em" }}>
                                <b>Mittelwerte und Standardabweichungen pro Subskala:</b>
                                <table style={{ width: "100%", marginTop: "0.5em", borderCollapse: "collapse" }}>
                                    <thead>
                                    <tr style={{ background: "#222", color: "#fff" }}>
                                        <th style={{ padding: "4px 8px", borderRadius: "4px 0 0 4px" }}>Subskala</th>
                                        <th style={{ padding: "4px 8px" }}>Mittelwert</th>
                                        <th style={{ padding: "4px 8px", borderRadius: "0 4px 4px 0" }}>Stdabw.</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {stats.map(row => (
                                        <tr key={row.item} style={{ background: "#23272f", color: "#fff" }}>
                                            <td style={{ padding: "4px 8px" }}>{row.item}</td>
                                            <td style={{
                                                padding: "4px 8px",
                                                fontWeight: "bold",
                                                color: "#fff"
                                            }}>{row.mean}</td>
                                            <td style={{
                                                padding: "4px 8px",
                                                fontWeight: "bold",
                                                color: "#fff"
                                            }}>{row.std}</td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    );
                })}
            </div>

            {diffData.length > 0 && (
                <div style={{display: "flex", gap: "2rem", marginTop: "2rem"}}>
                    <div style={{flex: 1}}>
                        <h3 className="mb-2">Differenz der Mittelwerte (Trial {trials[1][0]} -
                            Trial {trials[0][0]})</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={diffData}
                                      margin={{top: 20, right: 0, left: 0, bottom: 50}} // mehr Platz unten
                            >
                                <XAxis dataKey="item" interval={0} angle={-45} textAnchor="end"/>
                                <YAxis domain={[minDiff, maxDiff]}/>
                                <Tooltip
                                    contentStyle={{
                                        background: "#23272f",
                                        border: "1px solid #444",
                                        color: "#fff",
                                        borderRadius: "8px",
                                        boxShadow: "0 2px 8px #0004"
                                    }}
                                    itemStyle={{
                                        color: "#fff"
                                    }}
                                />
                                <Bar dataKey="diff" fill="#8884d8" name="Differenz">
                                    <LabelList dataKey="diff" position="top"/>
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div style={{flex: 1}}>
                        <h3 className="mb-2">Radar-Chart</h3>
                        {/*<ResponsiveContainer width="100%" height="100%">*/}
                        {/*    /!* Beispiel für ein RadarChart, passe die Daten ggf. an *!/*/}
                        {/*    <RadarChart data={radarData}>*/}
                        {/*        <PolarGrid/>*/}
                        {/*        <PolarAngleAxis dataKey="item"/>*/}
                        {/*        <PolarRadiusAxis/>*/}
                        {/*        {trials.map(([trial_id], idx) => (*/}
                        {/*            <Radar*/}
                        {/*                key={trial_id}*/}
                        {/*                name={`Trial ${trial_id}`}*/}
                        {/*                dataKey={`trial${idx + 1}`}*/}
                        {/*                stroke={idx === 0 ? "#8884d8" : "#82ca9d"}*/}
                        {/*                fill={idx === 0 ? "#8884d8" : "#82ca9d"}*/}
                        {/*                fillOpacity={0.3}*/}
                        {/*            />*/}
                        {/*        ))}*/}
                        {/*        <Tooltip*/}
                        {/*            contentStyle={{*/}
                        {/*                background: "#23272f",*/}
                        {/*                border: "1px solid #444",*/}
                        {/*                color: "#fff",*/}
                        {/*                borderRadius: "8px",*/}
                        {/*                boxShadow: "0 2px 8px #0004"*/}
                        {/*            }}*/}
                        {/*            itemStyle={{*/}
                        {/*                color: "#fff"*/}
                        {/*            }}*/}
                        {/*        />*/}
                        {/*    </RadarChart>*/}
                        {/*</ResponsiveContainer>*/}
                        <RadarChartPlotly
                            radarData={radarData}
                            trialLabels={trials.map(([trial_id]) => `Trial ${trial_id}`)}
                            range={questionnaireRange}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}