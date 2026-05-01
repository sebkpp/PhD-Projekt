import { useExperimentForm } from '../hooks/useExperimentForm.js'
import {useEffect, useRef} from "react";

export default function ExperimentForm({ studyGeneralInfo, onChange }) {



    const {
        description, setDescription,
        researcher, setResearcher,
        error,
    } = useExperimentForm(studyGeneralInfo)

    const prevValues = useRef({ description, researcher });


    useEffect(() => {
        if (
            prevValues.current.description !== description ||
            prevValues.current.researcher !== researcher
        ) {
            onChange({ description, principalInvestigator: researcher });
            prevValues.current = { description, researcher };
        }
    }, [description, researcher, onChange]);

    return (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow text-gray-900 dark:text-gray-100 transition-colors">
            <h1 className="text-2xl font-bold text-center mb-4">Generelle Informationen</h1>

            <div className="space-y-2">
                <label htmlFor="researcher" className="block text-sm mt-3">Versuchsleiter:in</label>
                <input
                    id="researcher"
                    type="text"
                    className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                    value={researcher}
                    onChange={(e) => setResearcher(e.target.value)}
                    placeholder="z.B. Mustermann"
                />

                <label htmlFor="description" className="block text-sm mt-3">Beschreibung (optional)</label>
                <textarea
                    id="description"
                    rows={3}
                    className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Detaillierte Beschreibung, Zielsetzung usw."
                />
            </div>

            {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
    )
}
