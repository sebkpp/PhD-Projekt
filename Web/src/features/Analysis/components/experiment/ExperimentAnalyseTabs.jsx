import React, { useState } from "react";

export function ExperimentAnalyseTabs({ tabs, defaultKey, onTabChange, children }) {
    const [activeKey, setActiveKey] = useState(defaultKey ?? tabs[0].key);

    function handleClick(key) {
        setActiveKey(key);
        onTabChange?.(key);
    }

    return (
        <div>
            <div className="flex gap-2 mb-6 flex-wrap">
                {tabs.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => handleClick(tab.key)}
                        className={`px-4 py-2 rounded transition-colors ${
                            activeKey === tab.key
                                ? "bg-blue-700 text-white"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            {React.Children.map(children, child =>
                React.cloneElement(child, { isActive: child.props.tabKey === activeKey })
            )}
        </div>
    );
}

// tabKey is intentionally not destructured here — the parent reads child.props.tabKey directly.
// eslint-disable-next-line no-unused-vars
export function TabPanel({ tabKey, children, isActive }) {
    return <div className={isActive ? "" : "hidden"}>{children}</div>;
}
