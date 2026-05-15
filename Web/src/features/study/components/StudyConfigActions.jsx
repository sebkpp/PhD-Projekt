import React from "react";
import { useTranslation } from "react-i18next";

export default function StudyConfigActions({ saving, onSaveDraft, onConfirm }) {
    const { t } = useTranslation('study');
    return (
        <div className="flex gap-4 justify-end">
            <button
                onClick={onSaveDraft}
                disabled={saving}
                className="px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg shadow-md"
            >
                {saving ? t('config.savingButton') : t('config.saveDraftButton')}
            </button>
            <button
                onClick={onConfirm}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg shadow-md"
            >
                {t('config.finalizeButton')}
            </button>
        </div>
    );
}
