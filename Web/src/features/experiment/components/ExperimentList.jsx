import ExperimentTile from "./ExperimentTile";
import { useTranslation } from 'react-i18next';

export default function ExperimentList({ experiments, study_id }) {
    const { t } = useTranslation('study');
    if (!experiments || experiments.length === 0) {
        return <p className="text-gray-400">{t('overview.noExperiments')}</p>;
    }
    const sortedExperiments = [...experiments].sort((a, b) => b.experiment_id - a.experiment_id);
    return (
        <div className="flex flex-col gap-6">
            {sortedExperiments.map((exp, idx) => (
                <ExperimentTile
                    key={exp.experiment_id}
                    experiment={exp}
                    study_id={study_id}
                    index={sortedExperiments.length - idx}
                />
            ))}
        </div>
    );
}
