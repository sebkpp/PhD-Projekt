export default function StudyOverviewActions({ onNewStudy, onStatistics }) {
    return (
        <div className="flex gap-2">
            <button
                onClick={onNewStudy}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
            >
                Neue Studie anlegen
            </button>
            <button
                onClick={onStatistics}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
            >
                Zur Auswertung
            </button>
        </div>
    );
}