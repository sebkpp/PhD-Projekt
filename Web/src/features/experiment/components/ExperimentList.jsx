import ExperimentTile from "./ExperimentTile";

export default function ExperimentList({ experiments, study_id }) {
  if (!experiments || experiments.length === 0) {
    return <p className="text-gray-400">Keine Experimente vorhanden.</p>;
  }

  const sortedExperiments = [...experiments].sort((a, b) => b.experiment_id - a.experiment_id);

  return (
    <div className="flex flex-col gap-6">
      {sortedExperiments.map((exp, idx) => (
        <ExperimentTile
            key={exp.experiment_id}
            experiment={exp}
            study_id={study_id}
            index={sortedExperiments.length - idx} />
      ))}
    </div>
  );
}