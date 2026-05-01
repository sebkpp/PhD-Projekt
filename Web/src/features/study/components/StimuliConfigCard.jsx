import React, {useMemo} from "react";
import {useAvatarOptions} from "@/features/configuration/components/useAvatarOptions.js";
import { stimuliIdToShortcode, shortcodeToStimuliId } from "../utils/stimuliUtils.jsx";

export default function StimuliConfigCard({ config, onChange }) {

    const activeStimuli = useMemo(() => {
        const result = {};
        (config?.stimuli ?? []).forEach(s => {
            const code = stimuliIdToShortcode[s.stimuli_type_id];
            if (code) result[code] = true;
        });
        return result;
    }, [config?.stimuli]);

    const { avatarOptions, error: avatarError } = useAvatarOptions()

    const handleStimuliChange = (type, checked) => {
        let newStimuli = [...(config?.stimuli ?? [])];
        const id = shortcodeToStimuliId[type];
        if (checked) {
            // Hinzufügen, falls nicht vorhanden
            if (!newStimuli.some(s => s.stimuli_type_id === id)) {
                newStimuli.push({ stimuli_type_id: id });
            }
        } else {
            // Entfernen
            newStimuli = newStimuli.filter(s => s.stimuli_type_id !== id);
        }
        onChange("stimuli", newStimuli);
    };

    return (
        <div className="rounded-2xl border border-border bg-gray-800 p-6 shadow-md mb-6">
            <h2 className="text-lg font-semibold mb-4">Studienweite Stimuli & Avatar</h2>
            <div className="mb-2 text-sm">
                <label className="block font-medium mb-1">Aktive Stimuli:</label>
                <div className="flex gap-4 rounded px-2 py-1">
                    {["vis", "aud", "tak"].map(type => (
                        <label key={type} className="flex items-center gap-1">
                            <input
                                type="checkbox"
                                checked={activeStimuli[type] || false}
                                onChange={e => handleStimuliChange(type, e.target.checked)}
                            />
                            <span>{type.toUpperCase()}</span>
                        </label>
                    ))}
                </div>
            </div>
            <div className="mb-2 text-sm">
                <label className="block font-medium mb-1">Avatarsichtbarkeit:</label>
                <select
                    className="bg-gray-700 rounded px-2 py-1 w-full"
                    value={config?.config?.avatar || ""}
                    onChange={e =>
                        onChange("config", {
                            ...config?.config,
                            avatar: e.target.value
                        })}
                >
                    <option value="">Bitte wählen</option>
                    {avatarOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
            </div>
            <div className="mb-2 text-sm flex gap-4">
                <div>
                    <label className="block font-medium mb-1">Anzahl der Trials:</label>
                    <input
                        type="number"
                        min={1}
                        className="bg-gray-700 rounded px-2 py-1 w-24"
                        value={config?.config?.trial_number ?? 1}
                        onChange={e => onChange("config", {
                            ...config?.config,
                            trial_number: Math.max(1, parseInt(e.target.value) || 1)
                        })}
                    />
                </div>
            </div>
            <div>
                <label className="block font-medium mb-1">Trials permutieren:</label>
                <input
                    type="checkbox"
                    checked={!!config?.config?.trials_permuted}
                    onChange={e => onChange("config", {
                        ...config?.config,
                        trials_permuted: e.target.checked})}
                    className="ml-2"
                />
                <span className="ml-1">{config?.config?.trials_permuted ? "Permutiert" : "Fixe Reihenfolge"}</span>
            </div>
        </div>
    );
}