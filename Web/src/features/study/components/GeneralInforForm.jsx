import { useTranslation } from 'react-i18next'

export default function GeneralInfoForm({ values, onChange }) {
    const { t } = useTranslation('study')

    return (
        <div className="bg-gray-800 rounded-lg p-6 mb-6 shadow-md">
            <h2 className="text-xl font-semibold mb-4">{t('generalInfo.title')}</h2>
            <div className="space-y-4">
                <div>
                    <label className="block text-gray-400 mb-1">{t('generalInfo.nameLabel')}</label>
                    <input
                        type="text"
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.name ?? ""}
                        onChange={e => onChange("config", { ...(values?.config ?? {}), name: e.target.value })}
                        placeholder={t('generalInfo.namePlaceholder')}
                        required
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">{t('generalInfo.piLabel')}</label>
                    <input
                        type="text"
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.principal_investigator ?? ""}
                        onChange={e => onChange("config", { ...(values?.config ?? {}), principal_investigator: e.target.value })}
                        placeholder={t('generalInfo.piPlaceholder')}
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">{t('generalInfo.descriptionLabel')}</label>
                    <textarea
                        rows={3}
                        className="w-full rounded px-3 py-2 bg-gray-700 text-gray-100 border border-gray-600"
                        value={values?.config?.description ?? ""}
                        onChange={e => onChange("config", { ...(values?.config ?? {}), description: e.target.value })}
                        placeholder={t('generalInfo.descriptionPlaceholder')}
                    />
                </div>
            </div>
        </div>
    );
}
