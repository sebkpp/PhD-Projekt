import { DateTime } from "luxon";

export function computePerformanceMetrics(handovers) {
    if (!handovers?.length) return null;

    let totalDuration = 0;
    let phase1Sum = 0, phase2Sum = 0, phase3Sum = 0;
    const objectStats = {};
    const participantStats = {};

    handovers.forEach(h => {
        const t1 = h.giver_grasped_object ? DateTime.fromISO(h.giver_grasped_object) : null;
        const t2 = h.receiver_touched_object ? DateTime.fromISO(h.receiver_touched_object) : null;
        const t3 = h.receiver_grasped_object ? DateTime.fromISO(h.receiver_grasped_object) : null;
        const t4 = h.giver_released_object ? DateTime.fromISO(h.giver_released_object) : null;

        const phase1 = t1 && t2 ? t2.diff(t1, "milliseconds").milliseconds : 0;
        const phase2 = t2 && t3 ? t3.diff(t2, "milliseconds").milliseconds : 0;
        const phase3 = t3 && t4 ? t4.diff(t3, "milliseconds").milliseconds : 0;
        const total = t1 && t4 ? t4.diff(t1, "milliseconds").milliseconds : 0;

        totalDuration += total;
        phase1Sum += phase1;
        phase2Sum += phase2;
        phase3Sum += phase3;

        // Objekt-Statistik
        objectStats[h.grasped_object] = objectStats[h.grasped_object] || { count: 0, duration: 0 };
        objectStats[h.grasped_object].count += 1;
        objectStats[h.grasped_object].duration += total;

        // Teilnehmer-Statistik (Giver)
        participantStats[h.giver] = participantStats[h.giver] || { count: 0, duration: 0 };
        participantStats[h.giver].count += 1;
        participantStats[h.giver].duration += total;
    });

    const avgDuration = totalDuration / handovers.length;
    const avgPhase1 = phase1Sum / handovers.length;
    const avgPhase2 = phase2Sum / handovers.length;
    const avgPhase3 = phase3Sum / handovers.length;

    // Für Charts: Arrays bauen
    const objectChart = Object.entries(objectStats).map(([obj, stat]) => ({
        object: obj,
        avgDuration: stat.duration / stat.count
    }));

    const participantChart = Object.entries(participantStats).map(([pid, stat]) => ({
        participant: pid,
        avgDuration: stat.duration / stat.count
    }));

    return {
        count: handovers.length,
        totalDuration,
        avgDuration,
        avgPhase1,
        avgPhase2,
        avgPhase3,
        objectChart,
        participantChart
    };
}

export async function fetchPerformanceMetrics(experimentId) {
    try {
        const response = await fetch(`/api/analysis/experiment/${experimentId}/performance`);
        if (!response.ok) return null;
        return await response.json();
    } catch {
        return null;
    }
}