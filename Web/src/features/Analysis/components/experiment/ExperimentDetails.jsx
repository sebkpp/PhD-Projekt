import React from "react";

function formatDate(dateString) {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("de-DE");
}

function formatTime(dateString) {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

function getDuration(start, end) {
    if (!start || !end) return "—";
    const startDate = new Date(start);
    const endDate = new Date(end);
    const diffMs = endDate - startDate;
    if (diffMs < 0) return "—";
    const min = Math.floor(diffMs / 60000);
    const h = Math.floor(min / 60);
    const m = min % 60;
    return h > 0 ? `${h}h ${m}min` : `${m}min`;
}

export default function ExperimentDetails({ experimentDetails }) {

    const {
        study_id,
        experiment_id,
        researcher,
        description,
        created_at,
        started_at,
        completed_at
    } = experimentDetails;

    return (
        <section className="w-full mb-8 p-4 bg-gray-900 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center gap-2 mb-2">
                <h2 className="text-xl font-bold text-blue-300">Experiment-Details</h2>
            </div>
            <div className="grid grid-cols-3 gap-2 mb-2">
                <div>
                    <div className="text-gray-400 text-xs">ID</div>
                    <div className="font-semibold text-gray-100 text-sm">{experiment_id}</div>
                </div>
                <div>
                    <div className="text-gray-400 text-xs">Study ID</div>
                    <div className="font-semibold text-gray-100 text-sm">{study_id}</div>
                </div>
                <div>
                    <div className="text-gray-400 text-xs">Versuchsleiter:in</div>
                    <div className="font-semibold text-gray-100 text-sm">{researcher || "—"}</div>
                </div>
            </div>
            <div className="flex items-center gap-2 mb-2">
                <div className="text-gray-400 text-xs">Erstellt am</div>
                <div className="font-semibold text-gray-100 text-sm">{formatDate(created_at)}</div>
            </div>
            <div className="flex items-center gap-2 mb-4">
                <div className="text-gray-400 text-xs">Uhrzeit</div>
                <div className="font-semibold text-gray-100 text-sm">{formatTime(started_at)}</div>
                <span className="text-gray-400">-</span>
                <div className="font-semibold text-gray-100 text-sm">{formatTime(completed_at)}</div>
                <span className="text-gray-400 text-xs">({getDuration(started_at, completed_at)})</span>
            </div>
            <div>
                <div className="text-gray-400 text-xs mb-1">Beschreibung</div>
                <div className="font-semibold text-gray-100 text-sm">{description || "—"}</div>
            </div>
        </section>
    );
}