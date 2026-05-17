import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import QuestionnaireSelector from "@/features/questionnaire/components/QuestionnaireSelector/questionnaireSelector";
import { useStudyConfig } from "@/features/study/hooks/useStudyConfig";
import SaveConfirmDialog from "@/features/study/components/SaveConfirmDialog";
import GeneralInfoForm from "@/features/study/components/GeneralInforForm.jsx";
import StudyConfigActions from "@/features/study/components/StudyConfigActions.jsx";
import StimuliConfigCard from "@/features/study/components/StimuliConfigCard.jsx";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";

export default function StudyConfigurationPage() {
    const { t } = useTranslation(['study', 'navigation']);
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
        const success = await saveConfig(status);
        setSaving(false);
        if (success) navigate('/');
    };

    const breadcrumbItems = [
        { label: t('navigation:breadcrumbs.studyOverview'), to: "/" },
        { label: t('study:config.newStudy') }
    ];

    return (
        <div className="p-6 min-h-screen bg-gray-900 text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6"/>
            <h1 className="text-2xl font-bold mb-6">{t('study:config.title')}</h1>
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
                <h2 className="text-xl font-semibold mb-4">{t('study:config.questionnairesSection')}</h2>
                <p className="text-gray-400 mb-2">{t('study:config.questionnairesHint')}</p>
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
                title={t('study:config.confirmTitle')}
                message={t('study:config.confirmMessage')}
                onCancel={() => setShowConfirm(false)}
                onConfirm={() => {
                    setShowConfirm(false);
                    handleSave("Aktiv");
                }}
            />
        </div>
    );
}
