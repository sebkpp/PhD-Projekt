using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Application.Scripts.Feedback.Data;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;

namespace Application.Scripts.Study
{
    /// <summary>
    /// Single HTTP layer for the entire Unity project.
    /// At Start: fetches active trial from backend (online) or serves from StudySessionConfig (offline).
    /// Fires OnSessionReady(SessionState) when data is ready — either from HTTP or from SO defaults.
    /// All reporting methods (ReportHandover, EndTrial) are fire-and-forget.
    /// Attach to the StudyManager prefab (replaces ExperimentContext).
    /// </summary>
    public class BackendService : MonoBehaviour
    {
        [SerializeField] private StudySessionConfig _config;

        public UnityEvent<SessionState> OnSessionReady  = new();
        public UnityEvent               OnStudyComplete = new();

        private int          _currentTrialIndex;
        private SessionState _currentSession;

        private void Start()
        {
            if (_config == null)
            {
                Debug.LogError("[BackendService] StudySessionConfig not assigned.");
                return;
            }

            if (_config.offlineMode)
                ActivateOfflineSession();
            else
                StartCoroutine(FetchSessionOnline());
        }

        // ── Offline path ─────────────────────────────────────────────────────────

        private void ActivateOfflineSession()
        {
            if (_config.trials == null || _config.trials.Length == 0)
            {
                Debug.LogWarning("[BackendService] offlineMode=true but no trials configured in StudySessionConfig.");
                return;
            }
            _currentTrialIndex = 0;
            FireSession(BuildSessionFromConfig(_config.trials[_currentTrialIndex]));
        }

        // ── Public API ───────────────────────────────────────────────────────────

        /// <summary>
        /// Call after a trial ends. Online: re-polls /experiments/next. Offline: advances to next TrialConfig.
        /// Fires OnStudyComplete when no more trials remain (offline only — online backend controls sequencing).
        /// </summary>
        public void AdvanceToNextTrial()
        {
            if (_config.offlineMode)
            {
                _currentTrialIndex++;
                if (_currentTrialIndex >= _config.trials.Length)
                {
                    OnStudyComplete?.Invoke();
                    return;
                }
                FireSession(BuildSessionFromConfig(_config.trials[_currentTrialIndex]));
            }
            else
            {
                StartCoroutine(FetchSessionOnline());
            }
        }

        /// <summary>
        /// Fire-and-forget: POSTs handover data to backend. On failure logs silently.
        /// In Editor with logHandoversLocally=true also writes a local JSON file.
        /// </summary>
        public void ReportHandover(HandoverData data)
        {
            LogHandoverLocally(data);
            if (!_config.offlineMode)
                StartCoroutine(PostHandover(data));
        }

        /// <summary>Fire-and-forget: notifies backend that the current trial is done.</summary>
        public void EndTrial(int trialId)
        {
            if (!_config.offlineMode)
                StartCoroutine(PostEndTrial(trialId));
        }

        // ── Online HTTP ──────────────────────────────────────────────────────────

        private IEnumerator FetchSessionOnline()
        {
            ExperimentNextResponse expResponse = null;
            while (expResponse == null)
            {
                using var req = UnityWebRequest.Get($"{_config.backendUrl}/experiments/next");
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    var parsed = JsonUtility.FromJson<ExperimentNextResponse>(req.downloadHandler.text);
                    if (parsed != null && parsed.trial_id > 0)
                        expResponse = parsed;
                    else
                        yield return new WaitForSeconds(_config.pollIntervalSeconds);
                }
                else
                {
                    Debug.LogWarning($"[BackendService] GET /experiments/next failed: {req.error}. Retrying in {_config.pollIntervalSeconds}s\u2026");
                    yield return new WaitForSeconds(_config.pollIntervalSeconds);
                }
            }

            StimulusSlotConfig[] stimuli = Array.Empty<StimulusSlotConfig>();
            using (var stimReq = UnityWebRequest.Get($"{_config.backendUrl}/trials/{expResponse.trial_id}/stimuli"))
            {
                yield return stimReq.SendWebRequest();
                if (stimReq.result == UnityWebRequest.Result.Success)
                    stimuli = StimulusSlotConfig.ParseArray(stimReq.downloadHandler.text);
                else
                    Debug.LogWarning($"[BackendService] GET /trials/stimuli failed: {stimReq.error}. Using empty stimuli.");
            }

            FireSession(BuildSessionFromOnlineData(expResponse, stimuli));
        }

        private IEnumerator PostHandover(HandoverData data)
        {
            string postBody = $"{{\"giver\":{data.GiverParticipantId},\"receiver\":{data.ReceiverParticipantId},\"grasped_object\":\"{data.GraspedObject}\"}}";
            using var postReq = new UnityWebRequest($"{_config.backendUrl}/handovers/trials/{data.TrialId}", "POST");
            postReq.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(postBody));
            postReq.downloadHandler = new DownloadHandlerBuffer();
            postReq.SetRequestHeader("Content-Type", "application/json");
            yield return postReq.SendWebRequest();

            if (postReq.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"[BackendService] POST handover failed: {postReq.error}");
                yield break;
            }

            var created = JsonUtility.FromJson<HandoverCreateResponse>(postReq.downloadHandler.text);
            if (created == null || created.handover_id <= 0)
            {
                Debug.LogError("[BackendService] POST handover: invalid handover_id in response.");
                yield break;
            }

            yield return StartCoroutine(PatchHandoverPhases(created.handover_id, data));
        }

        private IEnumerator PatchHandoverPhases(int handoverId, HandoverData data)
        {
            string body = data.IsError
                ? $"{{\"is_error\":true,\"error_type\":\"{data.ErrorType}\"}}"
                : BuildPhasesPatchBody(data);

            using var req = new UnityWebRequest($"{_config.backendUrl}/handovers/{handoverId}/phases", "PATCH");
            req.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[BackendService] PATCH handover phases failed: {req.error}");
        }

        private static string BuildPhasesPatchBody(HandoverData data)
        {
            var sb = new StringBuilder("{");
            sb.Append($"\"giver_grasped_object\":\"{Iso(data.GiverGraspedAt)}\",");
            sb.Append($"\"receiver_touched_object\":\"{Iso(data.ReceiverTouchedAt)}\",");
            sb.Append($"\"receiver_grasped_object\":\"{Iso(data.ReceiverGraspedAt)}\"");
            if (data.GiverReleasedAt.HasValue)
                sb.Append($",\"giver_released_object\":\"{Iso(data.GiverReleasedAt.Value)}\"");
            sb.Append("}");
            return sb.ToString();
        }

        private IEnumerator PostEndTrial(int trialId)
        {
            using var req = new UnityWebRequest($"{_config.backendUrl}/trials/{trialId}/end", "POST");
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[BackendService] POST /trials/{trialId}/end failed: {req.error}");
        }

        // ── Session construction ─────────────────────────────────────────────────

        private static SessionState BuildSessionFromConfig(TrialConfig config)
        {
            var slots = new Dictionary<int, SlotData>();
            foreach (var sc in config.slots)
            {
                var stimuli = BuildStimuliFromSlotConfig(sc);
                slots[sc.playerId] = new SlotData(sc.playerId, sc.gender, sc.participantId, stimuli);
            }
            return new SessionState(config.trialId, 0, slots);
        }

        private static StimulusSlotConfig BuildStimuliFromSlotConfig(SlotConfig sc)
        {
            var stimList = new System.Collections.Generic.List<TrialSlotStimulusData>();

            if (!string.IsNullOrEmpty(sc.visualStimulusName))
            {
                stimList.Add(new TrialSlotStimulusData
                {
                    stimulus = new StimulusData
                    {
                        stimulus_type = "visual",
                        name          = sc.visualStimulusName,
                        visuals       = new[] { sc.visualStimulusName },
                        auditives     = Array.Empty<AuditoryStimulusData>(),
                        tactiles      = Array.Empty<TactileStimulusData>()
                    }
                });
            }

            if (sc.hasAuditoryStimulus)
            {
                stimList.Add(new TrialSlotStimulusData
                {
                    stimulus = new StimulusData
                    {
                        stimulus_type = "auditory",
                        name          = "offline_audio",
                        visuals       = Array.Empty<string>(),
                        auditives     = new[] { new AuditoryStimulusData { frequency = sc.auditoryFrequency, volume = sc.auditoryVolume } },
                        tactiles      = Array.Empty<TactileStimulusData>()
                    }
                });
            }

            return new StimulusSlotConfig { slot = sc.playerId, stimuli = stimList.ToArray() };
        }

        private static SessionState BuildSessionFromOnlineData(ExperimentNextResponse exp, StimulusSlotConfig[] stimuli)
        {
            var stimuliBySlot = new Dictionary<int, StimulusSlotConfig>();
            foreach (var s in stimuli) stimuliBySlot[s.slot] = s;

            var slots = new Dictionary<int, SlotData>();
            foreach (var entry in exp.slots)
            {
                stimuliBySlot.TryGetValue(entry.slot, out var slotStimuli);
                slots[entry.slot] = new SlotData(entry.slot, entry.gender, entry.participant_id, slotStimuli);
            }
            return new SessionState(exp.trial_id, exp.experiment_id, slots);
        }

        private void FireSession(SessionState state)
        {
            _currentSession = state;
            OnSessionReady?.Invoke(state);
        }

        // ── Local logging (Editor only) ──────────────────────────────────────────

        private void LogHandoverLocally(HandoverData data)
        {
#if UNITY_EDITOR
            if (_config == null || !_config.logHandoversLocally) return;
            string filename = $"handover_log_{data.TrialId}_{DateTime.UtcNow:yyyyMMddHHmmss}.json";
            string path     = System.IO.Path.Combine(Application.persistentDataPath, filename);
            string json     = JsonUtility.ToJson(new HandoverLogEntry(data), true);
            System.IO.File.WriteAllText(path, json);
            Debug.Log($"[BackendService] Handover logged to: {path}");
#endif
        }

        // ── Nested serialization types ───────────────────────────────────────────

        [Serializable] private class ExperimentNextResponse
        {
            public int         experiment_id;
            public int         trial_id;
            public SlotEntry[] slots;
        }

        [Serializable] private class SlotEntry
        {
            public int    slot;
            public string gender;
            public int    participant_id;
        }

        [Serializable] private class HandoverCreateResponse { public int handover_id; }

        [Serializable] private class HandoverLogEntry
        {
            public int    trialId;
            public int    giverParticipantId;
            public int    receiverParticipantId;
            public string graspedObject;
            public string giverGraspedAt;
            public string receiverTouchedAt;
            public string receiverGraspedAt;
            public string giverReleasedAt;
            public bool   isError;
            public string errorType;

            public HandoverLogEntry(HandoverData d)
            {
                trialId               = d.TrialId;
                giverParticipantId    = d.GiverParticipantId;
                receiverParticipantId = d.ReceiverParticipantId;
                graspedObject         = d.GraspedObject;
                giverGraspedAt        = Iso(d.GiverGraspedAt);
                receiverTouchedAt     = Iso(d.ReceiverTouchedAt);
                receiverGraspedAt     = Iso(d.ReceiverGraspedAt);
                giverReleasedAt       = d.GiverReleasedAt.HasValue ? Iso(d.GiverReleasedAt.Value) : null;
                isError               = d.IsError;
                errorType             = d.ErrorType;
            }
        }

        private static string Iso(DateTime dt) => dt.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");
    }
}
