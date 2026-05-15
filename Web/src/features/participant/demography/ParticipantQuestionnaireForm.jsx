import { useTranslation } from 'react-i18next';

export default function ParticipantQuestionnaireForm({
                                                         age,
                                                         setAge,
                                                         gender,
                                                         setGender,
                                                         handedness,
                                                         setHandedness,
                                                         loading,
                                                         error,
                                                         submitted,
                                                         onSubmit,
                                                     }) {
    const { t } = useTranslation('participant');

    if (submitted) {
        return (
            <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
                <h1 className="text-2xl font-bold mb-4">{t('demography.successTitle')}</h1>
                <p>{t('demography.successText')}</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
            <div className="max-w-xl w-full">
                <h1 className="text-2xl font-bold mb-6 text-center">{t('demography.title')}</h1>
                <p className="text-sm text-gray-400 text-center mb-8">
                    {t('demography.subtitle')}
                </p>

                <div className="space-y-6">
                    {/* Alter */}
                    <div>
                        <label className="block font-semibold mb-1">{t('demography.age')}</label>
                        <input
                            type="number"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        />
                    </div>

                    {/* Geschlecht */}
                    <div>
                        <label className="block font-semibold mb-1">{t('demography.gender')}</label>
                        <select
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        >
                            <option value="">{t('demography.pleaseSelect')}</option>
                            <option value="male">{t('demography.male')}</option>
                            <option value="female">{t('demography.female')}</option>
                            <option value="diverse">{t('demography.diverse')}</option>
                        </select>
                    </div>

                    {/* Händigkeit */}
                    <div>
                        <label className="block font-semibold mb-1">{t('demography.handedness')}</label>
                        <select
                            value={handedness}
                            onChange={(e) => setHandedness(e.target.value)}
                            className="w-full bg-gray-800 border border-border rounded px-3 py-2"
                        >
                            <option value="">{t('demography.pleaseSelect')}</option>
                            <option value="right">{t('demography.rightHanded')}</option>
                            <option value="left">{t('demography.leftHanded')}</option>
                            <option value="ambi">{t('demography.ambidextrous')}</option>
                        </select>
                    </div>

                    {error && (
                        <p className="text-red-400 text-sm mt-1 text-center">
                            {error}
                        </p>
                    )}

                    <button
                        onClick={onSubmit}
                        disabled={loading}
                        className="mt-4 px-6 py-3 bg-accent text-white rounded hover:bg-green-600 transition-all w-full"
                    >
                        {loading ? t('demography.submittingButton') : t('demography.submitButton')}
                    </button>
                </div>
            </div>
        </div>
    )
}
