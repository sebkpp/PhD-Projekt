import { useState, useEffect } from "react";

export function useTabs(trialNumber, MAX_TRIALS = 10) {
    const [tabs, setTabs] = useState([{ name: "Trial 1" }]);
    const [activeIndex, setActiveIndex] = useState(0);

    useEffect(() => {
        if (trialNumber) {
            const initialTabs = Array.from(
                { length: Math.max(1, trialNumber) },
                (_, i) => ({ name: `Trial ${i + 1}` })
            );
            setTabs(initialTabs);
            setActiveIndex(0);
        }
    }, [trialNumber]);

    function addTab() {
        if (tabs.length < MAX_TRIALS) {
            setTabs([...tabs, { name: `Trial ${tabs.length + 1}` }]);
            setActiveIndex(tabs.length);
        }
    }

    function removeTab(index) {
        const updated = tabs.filter((_, i) => i !== index)
            .map((tab, i) => ({ ...tab, name: `Trial ${i + 1}` }));
        let newActive = activeIndex;
        if (activeIndex >= updated.length) {
            newActive = updated.length - 1;
        } else if (index === activeIndex) {
            newActive = Math.max(0, activeIndex - 1);
        }
        setTabs(updated);
        setActiveIndex(newActive);
    }

    return { tabs, activeIndex, setActiveIndex, addTab, removeTab, MAX_TRIALS };
}