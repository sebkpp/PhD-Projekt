import { DateTime } from "luxon";

function getPhaseDurations(entry) {
    const t1 = entry.giver_grasped_object ? DateTime.fromISO(entry.giver_grasped_object) : null;
    const t2 = entry.receiver_touched_object ? DateTime.fromISO(entry.receiver_touched_object) : null;
    const t3 = entry.receiver_grasped_object ? DateTime.fromISO(entry.receiver_grasped_object) : null;
    const t4 = entry.giver_released_object ? DateTime.fromISO(entry.giver_released_object) : null;

    const phase1 = t1 && t2 ? t2.diff(t1, "milliseconds").milliseconds : 0;
    const phase2 = t2 && t3 ? t3.diff(t2, "milliseconds").milliseconds : 0;
    const phase3 = t3 && t4 ? t4.diff(t3, "milliseconds").milliseconds : 0;
    const total = t1 && t4 ? t4.diff(t1, "milliseconds").milliseconds : 0;

    return { phase1, phase2, phase3, total };
}

export default function HandoverTableRow({ entry, index }) {
    const { phase1, phase2, phase3, total } = getPhaseDurations(entry);


    return (
        <tr className="bg-gray-800 hover:bg-gray-700 rounded-lg shadow-sm">
            <td className="px-2">{index + 1}</td>
            <td className="px-2">{entry.grasped_object ?? '-'}</td>
            <td className="px-2 text-center">{entry.giver ?? '-'}</td>
            <td className="px-2 text-center">{entry.receiver ?? '-'}</td>
            <td>
                <div className="grid grid-cols-4 gap-1">
    <span className="px-1 rounded bg-blue-900/40 text-blue-300 text-xs text-center leading-tight">
      <div>{phase1}</div>
      <div className="text-[10px] text-gray-400">ms</div>
    </span>
                    <span className="px-1 rounded bg-green-900/40 text-green-300 text-xs text-center leading-tight">
      <div>{phase2}</div>
      <div className="text-[10px] text-gray-400">ms</div>
    </span>
                    <span className="px-1 rounded bg-yellow-900/40 text-yellow-300 text-xs text-center leading-tight">
      <div>{phase3}</div>
      <div className="text-[10px] text-gray-400">ms</div>
    </span>
                    <span className="px-1 rounded bg-gray-700 text-gray-200 text-xs font-semibold text-center leading-tight">
      <div>{total}</div>
      <div className="text-[10px] text-gray-400">ms</div>
    </span>
                </div>
            </td>
        </tr>
    )
}
