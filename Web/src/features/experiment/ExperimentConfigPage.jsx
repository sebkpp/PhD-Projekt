import Breadcrumbs from "@/components/Breadcrumbs";
import ExperimentForm from "./components/ExperimentForm";
import { useParams, useNavigate } from "react-router-dom";
import TrialTabs from "@/features/experiment/components/TrialTabs.jsx";
import TrialParticipantsTile from "@/features/experiment/components/TrialParticipantsTile.jsx";
import {useTrialConfigs} from "@/features/experiment/hooks/useTrialConfigs.js";
import {useValidation} from "@/features/experiment/hooks/useValidation.js";
import {useTabs} from "@/features/experiment/hooks/useTabs.js";
import {useStudyConfig} from "@/features/study/hooks/useStudyConfig.js";
import {useState} from "react";
import {useExperiments} from "@/features/experiment/hooks/useExperiments.js";

export default function ExperimentConfigPage() {
    const { studyId } = useParams();
    const { localConfig } = useStudyConfig(studyId);

    const studyGeneralInfo = {
        principalInvestigator: localConfig?.config?.principal_investigator,
        description: localConfig?.config?.description
    };
    const [generalInfo, setGeneralInfo] = useState({});
    const { saveExperiment, error } = useExperiments(studyId);


    const navigate = useNavigate();

    const {
        tabs,
        activeIndex,
        setActiveIndex,
        addTab,
        removeTab,
        MAX_TRIALS
    } = useTabs(localConfig?.config?.trial_number);
    const {
        trialConfigs,
        setTrialConfigs,
        handleStimuliChange
    } = useTrialConfigs(activeIndex);
    const {
        errors,
        showError,
        setShowError,
        validationErrors,
        setValidationErrors,
        handleSaveExperiment
    } = useValidation(trialConfigs, tabs.length);

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: `Studie ${studyId}`, to: `/study/${studyId}/experiments` },
        { label: "Neues Experiment" }
    ];

    function onSave() {
        const mergedConfigs = {
            trialConfig: trialConfigs,
            researcher: generalInfo.principalInvestigator,
            description: generalInfo.description,
            study_id : studyId
        };

        if (handleSaveExperiment()) {
            saveExperiment(mergedConfigs)
                .then(result => {
                    if (result) {
                        console.log("Experiment erfolgreich gespeichert:", result);
                        navigate(`/study/${studyId}/experiments`);
                    }
                });
        }
    }

    function onChange(info){
        setGeneralInfo(info);
    }


    return (
        <div className="p-6 bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6"/>
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Neues Experiment konfigurieren</h1>
                <button
                    onClick={onSave}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg shadow-md"
                >
                   Experiment speichern
                </button>
            </div>
            {showError && validationErrors.length > 0 && (
                <div className="mt-4 bg-red-950 border border-red-700 p-4 rounded text-sm text-red-300 space-y-1">
                    <strong className="block text-red-400 mb-2">Bitte beheben Sie folgende Fehler:</strong>
                    {validationErrors.map((err, idx) => (
                        <div key={idx}>
                            • {err.message}
                        </div>
                    ))}
                </div>
            )}
            <div className="flex gap-8 w-full">
                <div className="flex-1">
                    <ExperimentForm studyGeneralInfo={studyGeneralInfo} onChange={onChange}/>
                </div>
                <div className="flex-1 min-w-[350px]">
                    <div className="border border-border rounded-xl">
                        <TrialTabs
                            tabs={tabs}
                            activeIndex={activeIndex}
                            setActiveIndex={setActiveIndex}
                            addTab={addTab}
                            removeTab={removeTab}
                            maxTrials={MAX_TRIALS}
                        />
                        <div className="p-4 border-t border-border bg-gray-800 rounded-b-xl">
                            {/* Tab-Inhalt */}
                            <div>
                                <TrialParticipantsTile
                                    allowedStimuli={localConfig?.stimuli}
                                    onChange={handleStimuliChange}
                                    trial_number={activeIndex}
                                    configs={trialConfigs[`Trial ${activeIndex + 1}`] || {}}
                                    validationErrors={validationErrors.filter(e => e.trialIndex === activeIndex)}
                                    showValidation={showError}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}