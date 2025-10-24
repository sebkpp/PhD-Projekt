import { useNavigate } from "react-router-dom";
import {useStudyParticipants} from "@/features/study/hooks/useStudyParticipants.js";

export default function StudyTile({ study, experimentCount, onDelete }) {
    const navigate = useNavigate();
    const { participants, loading } = useStudyParticipants(study?.study_id);

    if (!study) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6 flex flex-col justify-center items-center min-h-[140px] text-gray-400">
                Keine Studiendaten vorhanden
            </div>
        );
    }

    const statusColors = {
        "Entwurf": "bg-yellow-600 text-white",
        "Aktiv": "bg-green-600 text-white",
        "Abgeschlossen": "bg-gray-600 text-white",
    };
    const statusColor = statusColors[study.status] || "bg-gray-500 text-white";

    async function handleDelete(studyId) {
        await onDelete(studyId);
    }

    return (
        <div className="relative bg-gray-800 rounded-xl shadow-lg border border-gray-700 p-6 flex flex-col gap-4 transition-colors">

            {/* Header: Name + Status */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-gray-100">{study.config.name ?? ''}</h3>
                    <span className="text-xs text-gray-400">ID: {study.study_id}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded ${statusColor} text-sm font-semibold`}>
                        {study.status}
                    </span>
                    {study.status === "Entwurf" && (
                        <button
                            className="text-gray-400 hover:text-red-500 p-1 rounded transition-colors"
                            onClick={() => handleDelete(study.study_id)}
                            title="Studie löschen"
                            style={{ lineHeight: 0 }}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24">
                                <path stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                                      d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    )}
                </div>
            </div>

            {/* Infos + Buttons nebeneinander */}
            <div className="flex justify-between items-start gap-4">
                {/* Meta-Infos links */}
                <div className="flex flex-col gap-1 text-sm text-gray-300">
                    <div>
                        <span className="font-semibold">Experimente:</span> {experimentCount ?? 0}
                    </div>
                    <div>
                        <span className="font-semibold">Teilnehmer:</span> {participants.length ?? 0}
                    </div>
                    <div>
                        <span className="font-semibold">Erstellt am:</span>{" "}
                        {study.created_at ? new Date(study.created_at).toLocaleDateString() : "-"}
                    </div>
                    <div>
                        <span className="font-semibold">Beschreibung:</span>{" "}
                        {study.config.description
                            ? study.config.description.slice(0, 30) + (study.config.description.length > 30 ? "…" : "")
                            : "-"}
                    </div>

                </div>

                {/* Buttons rechts */}
                <div className="flex flex-col gap-2 min-w-[180px]">
                    <button
                        className={`py-2 rounded-lg shadow-md transition-colors ${
                            study.status === "Entwurf"
                                ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-500 text-white"
                        }`}
                        onClick={() =>
                            study.status !== "Entwurf" &&
                            navigate(`/study/${study.study_id}/experiments`)
                        }
                        disabled={study.status === "Entwurf"}
                    >
                        Experimente anzeigen
                    </button>
                    <button
                        className={`py-2 rounded-lg shadow-md transition-colors ${
                            study.status === "Entwurf"
                                ? "bg-yellow-600 hover:bg-yellow-500 text-white"
                                : "bg-gray-700 text-gray-400 cursor-not-allowed"
                        }`}
                        onClick={() =>
                            study.status === "Entwurf" &&
                            navigate(`/study/${study.study_id}/configure`)
                        }
                        disabled={study.status !== "Entwurf"}
                    >
                        Study konfigurieren
                    </button>
                </div>
            </div>
        </div>
    );
}
