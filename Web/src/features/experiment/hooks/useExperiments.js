import { useState, useEffect } from "react";
import {createExperiment, getExperimentsByStudy} from "../services/experimentService";

export function useExperiments(studyId) {
  const [experiments, setExperiments] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    getExperimentsByStudy(studyId).then(exps => {
      const sorted = [...exps].sort((a, b) => b.experiment_id - a.experiment_id);
      setExperiments(sorted);
    });
  }, [studyId]);


  async function saveExperiment(experimentSettings) {
    setError(null);
    try {
      const result = await createExperiment({ experimentSettings });
      return result;
    } catch (err) {
      setError(err.message || "Fehler beim Speichern des Experiments.");
      return null;
    }
  }

  return { experiments, saveExperiment, error };
}