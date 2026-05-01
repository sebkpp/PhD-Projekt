export default function TrialTabs({ tabs, activeIndex, setActiveIndex, addTab, removeTab, maxTrials }) {
    return (
        <div className="flex gap-2 overflow-x-auto px-4 pt-4 -mb-px">
            {tabs.map((tab, index) => (
                <div key={index} className="relative">
                    <button
                        onClick={() => setActiveIndex(index)}
                        className={`px-4 py-2 rounded-t border border-b-0 whitespace-nowrap ${
                            activeIndex === index
                                ? 'bg-accent text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        {tab.name}
                    </button>
                    {tabs.length > 1 && (
                        <button
                            onClick={() => removeTab(index)}
                            className="absolute -top-2 -right-2 bg-gray-700 text-white hover:bg-red-500 transition-colors rounded-full w-5 h-5 text-xs shadow"
                            title="Tab löschen"
                        >
                            ✕
                        </button>
                    )}
                </div>
            ))}
            {tabs.length < maxTrials && (
                <button
                    onClick={addTab}
                    className="px-4 py-2 bg-gray-800 text-gray-400 rounded-t hover:bg-gray-700"
                >
                    ➕
                </button>
            )}
        </div>
    );
}