import React from "react";

export default function GeneralInfoForm({ values, onChange }) {

    return (
        <div className="bg-gray-800 rounded-lg p-6 mb-6 shadow-md">
            <h2 className="text-xl font-semibold mb-4">Allgemeine Informationen</h2>
            <div className="space-y-4">
                <div>
                    <label className="block text-gray-400 mb-1">Name *</label>
                    <input
                        type="text"
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.name ?? ""}
                        onChange={e => onChange("config", { ...(values?.config ?? {}), name: e.target.value })}
                        placeholder="z.B. Studie zur visuellen Stimuli"
                        required
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Principal Investigator</label>
                    <input
                        type="text"
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.principal_investigator ?? ""}
                        onChange={e =>onChange("config", { ...(values?.config ?? {}), principal_investigator: e.target.value })}
                        placeholder="z.B. Mustermann"
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Beschreibung</label>
                    <textarea
                        rows={3}
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.description ?? ""}
                        onChange={e => onChange("config", { ...(values?.config ?? {}), description: e.target.value })}
                        placeholder="Kurze Beschreibung der Studie"
                    />
                </div>
            </div>
        </div>
    );
}