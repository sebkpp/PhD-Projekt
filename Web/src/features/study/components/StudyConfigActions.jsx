import React from "react";

export default function StudyConfigActions({ saving, onSaveDraft, onConfirm }) {
    return (
        <div className="flex gap-4 justify-end">
            <button
                onClick={onSaveDraft}
                disabled={saving}
                className="px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg shadow-md"
            >
                {saving ? "Speichern..." : "Als Entwurf speichern"}
            </button>
            <button
                onClick={onConfirm}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg shadow-md"
            >
                Studienkonfiguration abschließen
            </button>
        </div>
    );
}