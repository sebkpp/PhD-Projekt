export function groupChartData(trialItemStats) {
    const grouped = {};
    Object.entries(trialItemStats).forEach(([trialId, trialStats]) => {
        const questionnaires = trialStats.questionnaires || {};
        Object.entries(questionnaires).forEach(([qName, qStats]) => {
            const items = qStats.items || {};
            const data = Object.entries(items).map(([, stats]) => ({
                item: stats.item_name,
                mean: Math.round(stats.mean * 10) / 10,
                std: Math.round(stats.std * 10) / 10
            }));
            grouped[qName] = grouped[qName] || [];
            grouped[qName].push([trialId, data]);
        });
    });
    // Rückgabe: [ [name, [ [trialId, data], ... ] ], ... ]
    return Object.entries(grouped);
}

export function getMaxValue(name) {
    if (name.toLowerCase().includes("tlx")) return 100;
    if (name.toLowerCase().includes("likert")) return 5;
    return 10;
}