import React, { useState } from "react";

export function ExperimentAnalyseTabs({ tabs, defaultKey, children }) {
    const [activeKey, setActiveKey] = useState(defaultKey ?? tabs[0].key);

    return (
        <div>
            <div className="flex gap-2 mb-6">
                {tabs.map(tab => (
                    <button
                        key={tab.key}
                        className={`px-4 py-2 rounded ${activeKey === tab.key ? "bg-blue-700 text-white" : "bg-gray-700 text-gray-300"}`}
                        onClick={() => setActiveKey(tab.key)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            {React.Children.map(children, child =>
                child.props.tabKey === activeKey ? child : null
            )}
        </div>
    );
}

export function TabPanel({ children }) {
    return <div>{children}</div>;
}