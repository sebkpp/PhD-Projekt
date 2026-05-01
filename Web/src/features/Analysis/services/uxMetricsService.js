
export async function fetchUxMetrics(experimentId) {
  const response = await fetch(`/api/analysis/experiment/${experimentId}/questionnaires`);
  if (!response.ok) {
    throw new Error(`Fehler beim Laden der UX-Metriken: ${response.statusText}`);
  }
  return await response.json();
}