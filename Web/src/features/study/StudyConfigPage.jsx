import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import QuestionnaireSelector from "@/features/questionnaire/components/QuestionnaireSelector/questionnaireSelector";
import { useStudyConfig } from "@/features/study/hooks/useStudyConfig";
import SaveConfirmDialog from "@/features/study/components/SaveConfirmDialog";
import GeneralInfoForm from "@/features/study/components/GeneralInforForm.jsx";
import StudyConfigActions from "@/features/study/components/StudyConfigActions.jsx";
import StimuliConfigCard from "@/features/study/components/StimuliConfigCard.jsx";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";

export default function StudyConfigurationPage() {
    const { studyId } = useParams();
    const navigate = useNavigate();
    const [saving, setSaving] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const {
        localConfig,
        error,
        updateLocalConfig,
        saveConfig } = useStudyConfig(studyId);

    const handleSave = async (status) => {
        setSaving(true);
        await saveConfig(status);
        setSaving(false);
        navigate('/');
    };

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Neue Studie" }
    ];

    return (
        <div className="p-6 min-h-screen bg-gray-900 text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6"/>
            <h1 className="text-2xl font-bold mb-6">Studie konfigurieren</h1>
            <div className="flex gap-6 mb-6">
                <div className="flex-1">
                    <GeneralInfoForm
                        values={localConfig}
                        onChange={updateLocalConfig}
                    />
                </div>
                <div className="flex-1">
                    <StimuliConfigCard
                        config={localConfig}
                        onChange={updateLocalConfig}
                    />
                </div>
            </div>

            {/* Fragebögen */}
            <div className="bg-gray-800 rounded-lg p-6 mb-6 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Fragebögen</h2>
                <p className="text-gray-400 mb-2">Wählen Sie die Fragebögen aus, die für alle Experimente gelten sollen.</p>
                <QuestionnaireSelector
                    selectedQuestionnaires={localConfig?.questionnaires ?? []}
                    onChange={(q) => updateLocalConfig("questionnaires", q)}
                />
            </div>

            {error && <p className="text-red-400 mb-4">{error}</p>}

            <StudyConfigActions
                saving={saving}
                onSaveDraft={() => handleSave("Entwurf")}
                onConfirm={() => setShowConfirm(true)}
            />

            <SaveConfirmDialog
                open={showConfirm}
                title={"Studiekonfiguration abschließen"}
                message={"Sind Sie sicher, dass Sie die Konfiguration der Studie abschließen möchten? Danach können keine Änderungen mehr gemacht werden."}
                onCancel={() => setShowConfirm(false)}
                onConfirm={() => {
                    setShowConfirm(false);
                    handleSave("Aktiv");
                }}
            />
        </div>
    );
}
