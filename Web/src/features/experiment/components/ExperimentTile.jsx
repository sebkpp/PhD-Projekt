import {Calendar, UserCog, Hash, Layers, Clock} from "lucide-react";
import dayjs from "dayjs";
import {useNavigate} from "react-router-dom";
import duration from "dayjs/plugin/duration";
import StimulusIcon from "@/features/study/utils/stimuliUtils.jsx";

dayjs.extend(duration);

export default function ExperimentTile({experiment, study_id, index, onOpen, onViewData}) {
    const navigate = useNavigate();
    const {
        experiment_id,
        researcher,
        description,
        created_at,
        started_at,
        completed_at,
        trials,
    } = experiment;

    const isFinished = !!completed_at;

    const formatDateTime = (date) =>
        date ? dayjs(date).format("DD.MM.YYYY HH:mm") : "–";

    let durationText = "–";
    if (started_at && completed_at) {
        const diffMs = dayjs(completed_at).diff(dayjs(started_at));
        const d = dayjs.duration(diffMs);
        durationText = `${d.hours()}h ${d.minutes()}min`;
    }

    return (
        <div
            className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-md border border-gray-700 p-4 hover:shadow-lg transition flex flex-col justify-between">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2">
                    <span> {index}. Experiment</span>
                    <span className="text-sm text-gray-400">(ID: {experiment_id})</span>
                </h2>
                <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        isFinished
                            ? "bg-gray-700 text-gray-300"
                            : "bg-green-900 text-green-200"
                    }`}
                >
                    {isFinished ? "Beendet" : "Offen"}
                </span>
            </div>

            {/* Details */}
            <div className="grid grid-cols-1 gap-2 text-gray-300 text-sm mb-4">
                <div className="flex items-center gap-2">
                    <UserCog className="w-4 h-4 text-orange-400"/>
                    <span className="font-medium">Versuchsleiter:in:</span>
                    <span>{researcher || "Unbekannt"}</span>
                </div>

                <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-purple-400"/>
                    <span className="font-medium">Datum:</span>
                    <span>{formatDateTime(created_at).split(" ")[0]}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="font-medium">Uhrzeiten:</span>
                    {started_at ? (
                        <span>{dayjs(started_at).format("HH:mm")}</span>
                    ) : (
                        <span className="flex items-center gap-1 text-gray-400">
            <Clock className="w-4 h-4" />
            Noch nicht gestartet
        </span>
                    )}
                    <span>–</span>
                    {completed_at ? (
                        <span>{dayjs(completed_at).format("HH:mm")}</span>
                    ) : (
                        <span className="flex items-center gap-1 text-gray-400">
            <Clock className="w-4 h-4" />
            Noch nicht beendet
        </span>
                    )}
                    {started_at && completed_at && (
                        <span className="ml-2 text-xs text-gray-400">
            ({durationText})
        </span>
                    )}
                </div>
            </div>

            {/* Beschreibung */}
            {description && (
                <>
                    <h3 className="font-medium text-gray-300 text-sm mb-1">Beschreibung:</h3>
                    <div className="bg-gray-800 rounded-lg p-3 mb-4 border border-gray-700 flex items-start gap-2">
                        <p className="text-gray-100 text-sm line-clamp-3">{description}</p>
                    </div>
                </>
            )}

            {/* Trial Übersicht */}
            {trials.length > 0 && (
                <div className="mb-4">
                    <h3 className="text-gray-300 text-xs mb-1 font-medium flex items-center gap-1">
                        <Layers className="w-3 h-3 text-yellow-400"/>
                        Trial Übersicht
                    </h3>
                    <div
                        className="flex flex-col gap-2 max-h-36 overflow-y-auto trial-scrollbar">                        {trials.map((trial) => (
                        <div
                            key={trial.trial_id}
                            className="bg-gray-700 text-gray-200 text-xs rounded px-2 py-1"
                        >
                            <div className="flex items-center gap-1 font-medium text-gray-300 mb-1">
                                <Hash className="w-3 h-3 text-blue-400"/>
                                Trial {trial.trial_number}
                            </div>
                            <div className="flex gap-2">
                                <div className="flex-1 flex flex-col gap-1">
    <span className="font-medium text-gray-400 text-[10px]">
      Slot {trial.slots[0].slot}:
    </span>
                                    <div className="flex flex-wrap gap-1">
                                        {trial.slots[0].stimuli.map((s) => (
                                            <span
                                                key={s.stimulus_id}
                                                className="flex items-center gap-1 bg-gray-800 rounded px-1 py-0.5 text-[10px]"
                                            >
          <StimulusIcon type={s.stimulus_type}/>
                                                {s.name}
        </span>
                                        ))}
                                    </div>
                                </div>
                                <div className="w-px bg-gray-500 mx-2 my-1"></div>
                                <div className="flex-1 flex flex-col gap-1">
    <span className="font-medium text-gray-400 text-[10px]">
      Slot {trial.slots[1].slot}:
    </span>
                                    <div className="flex flex-wrap gap-1">
                                        {trial.slots[1].stimuli.map((s) => (
                                            <span
                                                key={s.stimulus_id}
                                                className="flex items-center gap-1 bg-gray-800 rounded px-1 py-0.5 text-[10px]"
                                            >
          <StimulusIcon type={s.stimulus_type}/>
                                                {s.name}
        </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                    </div>
                </div>
            )}

            {/* Actions */}
            <button
                onClick={() => {
                    isFinished ? navigate(`/study/${study_id}/experiment/${experiment_id}/analysis`):
                        navigate(`/study/${study_id}/experiment/${experiment_id}/overview`);
                }} className={`w-full px-3 py-1.5 rounded-lg font-medium text-sm transition-colors ${
                isFinished
                    ? "bg-green-600 hover:bg-green-500 text-white"
                    : "bg-blue-600 hover:bg-blue-500 text-white"
            }`}
            >
                {isFinished ? "Daten-Übersicht ansehen" : "Zum Experiment"}
            </button>
        </div>
    );
}
