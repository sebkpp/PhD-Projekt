import { useState } from "react";
import StudyTile from "./components/StudyTile";
import { useNavigate } from "react-router-dom";
import DeleteConfirmModal from "./components/DeleteConfirmModal";
import { useStudies } from "./hooks/useStudies";
import StudyOverviewActions from "@/features/study/components/StudyOverviewActions.jsx";
import Breadcrumbs from "@/components/Breadcrumbs";

export default function StudyOverview() {
    const breadcrumbItems = [{ label: "Studienübersicht" }];

    const { studies, loading, error, removeStudy } = useStudies();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleteId, setDeleteId] = useState(null);
    const navigate = useNavigate();
    function askDelete(studyId) {
        setDeleteId(studyId);
        setShowDeleteConfirm(true);
    }

    async function confirmDelete() {
        await removeStudy(deleteId);
        setShowDeleteConfirm(false);
        setDeleteId(null);
    }

    function cancelDelete() {
        setShowDeleteConfirm(false);
        setDeleteId(null);
    }


    return (
        <div className="p-6 min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6"/>
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 transition-colors">Studienübersicht</h1>
                <StudyOverviewActions
                    onNewStudy={() => navigate("/study/configure")}
                    onStatistics={() => navigate("/analysis")}
                />
            </div>

            {error && (
                <div className="bg-red-100 dark:bg-red-900 rounded-lg shadow p-5 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-200 transition-colors mb-4">
                    {error}
                </div>
            )}

            {!loading && !error && (
                <div className="grid gap-4">
                    {studies.length === 0 ? (
                        <StudyTile />
                    ) : (
                        studies.map((study) => (
                            <StudyTile
                                key={study.study_id}
                                study={study}
                                experimentCount={study.experiments.length}
                                onDelete={() => askDelete(study.study_id)}
                            />
                        ))
                    )}
                </div>
            )}

            <DeleteConfirmModal
                open={showDeleteConfirm}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />
        </div>
    );
}
