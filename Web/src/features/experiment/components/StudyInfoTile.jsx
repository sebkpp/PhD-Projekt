import { Users, FlaskConical, UserCog, ClipboardList } from "lucide-react";
import {useCloseStudy} from "@/features/experiment/hooks/useCloseStudy.js";
import SaveConfirmDialog from "@/features/study/components/SaveConfirmDialog";
import {useEffect, useState} from "react";
import StimulusIcon from "@/features/study/utils/stimuliUtils.jsx";
import { useTranslation } from 'react-i18next';

export default function StudyInfoTile({
                                          studyId,
                                          name,
                                          description,
                                          status,
                                          onStatusChange,
                                          startDate,
                                          endDate,
                                          experimentCount,
                                          participantCount,
                                          researcher,
                                          stimuliTypes,
                                          questionnaires,
                                      }) {

    const statusColors = {
        active: "border-green-500 shadow-green-500/30",
        finished: "border-gray-500 shadow-gray-500/30",
        pending: "border-yellow-500 shadow-yellow-500/30",
    };

    const { t } = useTranslation('experiment');
    const { close, loading, error, result } = useCloseStudy(studyId);
    const [showCloseDialog, setShowCloseDialog] = useState(false);
    const isFinished = status === "Beendet";

    return (
        <div
            className={`rounded-2xl p-6 
        bg-gradient-to-br from-gray-800 to-gray-900 
        border-2 ${statusColors[status] || "border-gray-700"} 
        shadow-lg`}
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <ClipboardList className="w-5 h-5 text-blue-400" />
                    {t('studyInfo.title')}
                </h2>
                <span
                    className={`px-3 py-1 text-sm rounded-full ${
                        status === "Aktiv"
                            ? "bg-green-600 text-white"
                            : status === "Beendet"
                                ? "bg-gray-600 text-gray-200"
                                : "bg-yellow-600 text-white"
                    }`}
                >
          {status}
        </span>
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-2 gap-y-3 text-sm">
                <span className="text-gray-400">{t('studyInfo.studyId')}</span>
                <span className="text-gray-100">{studyId}</span>

                <span className="text-gray-400">{t('studyInfo.name')}</span>
                <span className="text-gray-100">{name}</span>

                <span className="text-gray-400">{t('studyInfo.description')}</span>
                <span className="text-gray-100">{description}</span>

                <span className="text-gray-400">{t('studyInfo.start')}</span>
                <span className="text-gray-100">
          {startDate || t('studyInfo.notStarted')}
        </span>

                <span className="text-gray-400">{t('studyInfo.end')}</span>
                <span className="text-gray-100">
          {endDate || t('studyInfo.notFinished')}
        </span>

                <span className="text-gray-400 flex items-center gap-1">
          <FlaskConical className="w-4 h-4 text-purple-400" />
          {t('studyInfo.experiments')}
        </span>
                <span className="text-gray-100">{experimentCount}</span>

                <span className="text-gray-400 flex items-center gap-1">
          <Users className="w-4 h-4 text-teal-400" />
          {t('studyInfo.participants')}
        </span>
                <span className="text-gray-100">{participantCount}</span>


                <span className="text-gray-400 flex items-center gap-1">
          <UserCog className="w-4 h-4 text-orange-400" />
          {t('studyInfo.researcher')}
        </span>
                <span className="text-gray-100">{researcher}</span>

            </div>

            {/* Stimuli */}
            <div className="mt-5">
                <h3 className="text-gray-300 text-sm mb-2">{t('studyInfo.stimuli')}</h3>
                <div className="flex flex-wrap gap-2">
                    {stimuliTypes?.length > 0 ? (
                        stimuliTypes.map((s, i) => (
                            <span
                                key={i}
                                className="flex items-center gap-2 bg-gray-700 px-3 py-1 rounded-full text-xs text-gray-200"
                            >
                                <StimulusIcon type={s.name} />
                              {s.name}
                            </span>
                        ))
                    ) : (
                        <span className="text-gray-500 text-sm">{t('studyInfo.none')}</span>
                    )}
                </div>
            </div>

            {/* Fragebögen */}
            <div className="mt-5">
                <h3 className="text-gray-300 text-sm mb-2">{t('studyInfo.questionnaires')}</h3>
                <div className="flex flex-wrap gap-2">
                    {questionnaires?.length > 0 ? (
                        questionnaires.map((q) => (
                            <span
                                key={q.questionnaire_id}
                                className="bg-blue-700 px-3 py-1 rounded-full text-xs text-white"
                            >
                {q.name}
              </span>
                        ))
                    ) : (
                        <span className="text-gray-500 text-sm">{t('studyInfo.none')}</span>
                    )}
                </div>
            </div>


            {/* Button zum Schließen der Studie */}

                <div className="mt-8 flex flex-col items-center">
                    <button
                        onClick={() => setShowCloseDialog(true)}
                        disabled={loading || isFinished}
                        className="px-6 py-3 bg-red-600 text-white rounded hover:bg-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {t('studyInfo.closeStudy')}
                    </button>
                    {error && <span className="text-red-400 mt-2">{t('studyInfo.error', { msg: error.message || error.toString() })}</span>}
                    {result && <span className="text-green-400 mt-2">{t('studyInfo.closedSuccess')}</span>}
                </div>

            <SaveConfirmDialog
                open={showCloseDialog}
                title={t('studyInfo.closeStudyTitle')}
                message={t('studyInfo.closeStudyMessage')}
                onCancel={() => setShowCloseDialog(false)}
                onConfirm={ async () => {
                    setShowCloseDialog(false);
                    await close();
                    onStatusChange("Beendet");
                }}
            />
        </div>
    );
}
