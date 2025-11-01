import {useNavigate, useParams} from "react-router-dom";
import Breadcrumbs from "@/components/Breadcrumbs";
import StudyInfoTile from "@/features/experiment/components/StudyInfoTile.jsx";
import {useExperiments} from "@/features/experiment/hooks/useExperiments.js";
import ExperimentHeaderActions from "@/features/experiment/components/ExperimentHeaderActions.jsx";
import ExperimentList from "@/features/experiment/components/ExperimentList.jsx";
import {useStudyConfig} from "@/features/study/hooks/useStudyConfig.js";
import {useStudyParticipants} from "@/features/study/hooks/useStudyParticipants.js";
import {useEffect, useState} from "react";

export default function ExperimentOverview() {
    const { studyId } = useParams();
    const navigate = useNavigate();
    const { experiments } = useExperiments(studyId);
    const { localConfig } = useStudyConfig(studyId);
    const { participants, loading } = useStudyParticipants(studyId);
    const [localStatus, setLocalStatus] = useState(localConfig?.status);

    function handleNewExperiment() {
        navigate(`/study/${studyId}/experiment/configure`);
    }

    function handleStatusChange(newStatus) {
        setLocalStatus(newStatus);
    }

    useEffect(() => {
        if (localConfig?.status) {
            setLocalStatus(localConfig.status);
        }
    }, [localConfig?.status]);

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: `Studie ${studyId}` }
    ];

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6"/>
            {/* Header mit Buttons */}
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Experimente</h1>
                <ExperimentHeaderActions
                    onNewExperiment={handleNewExperiment}
                    onEvaluate={() => navigate(`/study/${studyId}/analysis`)}
                    studyStatus={localStatus}
                />
            </div>

            {/* Zweispaltiges Layout */}
            <div className="flex gap-6">
                {/* Linke Spalte: Experimente */}
                <div className="flex-[2]">
                    <ExperimentList experiments={experiments} study_id={studyId}  />
                </div>

                {/* Rechte Spalte: Studien-Info */}
                {localConfig && (
                    <div className="flex-1">
                        <div className="sticky top-6">
                            <StudyInfoTile
                                studyId={studyId}
                                name={localConfig.config.name}
                                description={localConfig.config.description}
                                startDate={localConfig.started_at}
                                endDate={localConfig.ended_at}
                                status={localStatus}
                                onStatusChange={handleStatusChange}
                                experimentCount={experiments.length}
                                participantCount={loading ? "..." : participants.length}
                                researcher={localConfig.config.principal_investigator}
                                stimuliTypes={localConfig?.stimuli ?? []}
                                questionnaires={localConfig.questionnaires}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
