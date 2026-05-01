const BASE_URL =  "/api/studies";

/**
 * Verarbeitet die API-Antwort und wirft bei Fehlern eine Exception.
 * @param {Response} res - Die Fetch-Response.
 * @param {string} errorMsg - Fehlermeldung für den Fehlerfall.
 * @returns {Promise<any>} - Die Antwortdaten als JSON oder null.
 * @throws {Error} - Bei HTTP-Fehlern.
 */
async function handleResponse(res, errorMsg) {
  if (!res.ok) {
    throw new Error(`${errorMsg}: ${res.statusText}`);
  }
  return res.status === 204 ? null : await res.json();
}

/**
 * Lädt alle Studien.
 * @returns {Promise<Array>} - Liste der Studien.
 */
export async function fetchStudies() {
  const res = await fetch(BASE_URL);
  return handleResponse(res, "Fehler beim Laden der Studien");
}

/**
 * Lädt eine Studie anhand der ID.
 * @param {number|string} studyId - Die Studien-ID.
 * @returns {Promise<Object>} - Die Studien-Daten.
 */
export async function fetchStudyById(studyId) {
  const res = await fetch(`${BASE_URL}/${studyId}`);
  return handleResponse(res, `Fehler beim Laden der Studie ${studyId}`);
}

export async function fetchParticipants(studyId) {
  const res = await fetch(`${BASE_URL}/${studyId}/participants`);
  return handleResponse(res, `Fehler beim Laden der Teilnehmer für Studie ${studyId}`);
}

export async function closeStudy(studyId) {
  const res = await fetch(`${BASE_URL}/${studyId}/close`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  return handleResponse(res, `Fehler beim Schließen der Studie ${studyId}`);
}

/**
 * Sendet eine Studie per POST/PUT/DELETE an die API.
 * @param {string} method - HTTP-Methode ("POST", "PUT", "DELETE").
 * @param {string} url - Ziel-URL.
 * @param {Object|null} data - Zu sendende Daten.
 * @param {string} errorMsg - Fehlermeldung für Fehlerfall.
 * @returns {Promise<any>} - Antwortdaten.
 */
async function sendStudy(method, url, data, errorMsg) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return handleResponse(res, errorMsg);
}



/**
 * Erstellt eine neue Studie.
 * @param {Object} data - Die Studien-Daten.
 * @returns {Promise<Object>} - Die erstellte Studie.
 */
export async function createStudy(data) {
  return sendStudy(
      "POST",
      BASE_URL,
      data,
      "Fehler beim Erstellen der Studie");
}

/**
 * Aktualisiert eine bestehende Studie.
 * @param {number|string} studyId - Die Studien-ID.
 * @param {Object} data - Die neuen Studien-Daten.
 * @returns {Promise<Object>} - Die aktualisierte Studie.
 */
export async function updateStudy(studyId, data) {
  return sendStudy(
      "PUT",
      `${BASE_URL}/${studyId}`,
      data,
      `Fehler beim Aktualisieren der Studie ${studyId}`);
}

/**
 * Löscht eine Studie.
 * @param {number|string} studyId - Die Studien-ID.
 * @returns {Promise<null>} - Null bei Erfolg.
 */
export async function deleteStudy(studyId) {
  const res = await fetch(`${BASE_URL}/${studyId}`, {
    method: "DELETE"
  });
  return handleResponse(res, `Fehler beim Löschen der Studie ${studyId}`);
}