import React from "react";

export default function ExperimentHeaderActions({ onNewExperiment, onEvaluate, studyStatus }) {
    return (
    <div className="flex gap-4">
      <button
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!studyStatus || studyStatus === "Beendet"}
          onClick={onNewExperiment}
      >
        Neues Experiment anlegen
      </button>
      <button
        className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded-lg shadow-md"
        onClick={onEvaluate}
      >
        Zur Auswertung
      </button>
    </div>
  );
}