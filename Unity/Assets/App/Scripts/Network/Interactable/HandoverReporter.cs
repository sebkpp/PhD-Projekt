using System;
using System.Collections;
using System.Text;
using Application.Scripts.Network.Experiment;
using Fusion;
using UnityEngine;
using UnityEngine.Networking;

namespace Application.Scripts.Network.Interactable
{
    /// <summary>
    /// Persists handover events to the backend database.
    ///
    /// Subscribes to HandoverTracker C# events and NetworkGrabbableObject.onObjectDropped.
    /// Only the giver-client sends HTTP (identified by comparing Runner.LocalPlayer.PlayerId
    /// against the giver's PlayerId received in the GiverGrabbed event).
    ///
    /// Lifecycle:
    ///   ReceiverGrabbed  → POST /handovers/trials/{trialId}    → stores _activeHandoverId
    ///                    → PATCH /{id}/phases (3 timestamps)
    ///   GiverReleased    → PATCH /{id}/phases (giver_released_object) → reset
    ///   onObjectDropped  → PATCH /{id}/phases (is_error=true)         → reset
    /// </summary>
    public class HandoverReporter : MonoBehaviour
    {
        [SerializeField] private ExperimentContext _experimentContext;

        private HandoverTracker        _tracker;
        private NetworkGrabbableObject _netGrabbable;

        private int _giverPlayerId    = -1;
        private int _receiverPlayerId = -1;
        private int _activeHandoverId = -1;

        private DateTime _giverGrabbedAt;
        private DateTime _receiverTouchedAt;
        private DateTime _receiverGrabbedAt;
        private DateTime? _pendingGiverReleasedAt;
        private bool      _pendingDropError;

        private void Awake()
        {
            _tracker      = GetComponent<HandoverTracker>();
            _netGrabbable = GetComponent<NetworkGrabbableObject>();
            if (_experimentContext == null)
                Debug.LogError("[HandoverReporter] ExperimentContext reference not set — participant IDs will be -1.");
        }

        private void OnEnable()
        {
            if (_tracker != null)
            {
                _tracker.OnGiverGrabbedEvent    += HandleGiverGrabbed;
                _tracker.OnReceiverTouchedEvent += HandleReceiverTouched;
                _tracker.OnReceiverGrabbedEvent += HandleReceiverGrabbed;
                _tracker.OnGiverReleasedEvent   += HandleGiverReleased;
            }
            if (_netGrabbable != null)
                _netGrabbable.onObjectDropped.AddListener(HandleObjectDropped);
        }

        private void OnDisable()
        {
            if (_tracker != null)
            {
                _tracker.OnGiverGrabbedEvent    -= HandleGiverGrabbed;
                _tracker.OnReceiverTouchedEvent -= HandleReceiverTouched;
                _tracker.OnReceiverGrabbedEvent -= HandleReceiverGrabbed;
                _tracker.OnGiverReleasedEvent   -= HandleGiverReleased;
            }
            if (_netGrabbable != null)
                _netGrabbable.onObjectDropped.RemoveListener(HandleObjectDropped);
        }

        // True only on the client whose local player is the giver
        private bool IsGiverClient =>
            _tracker != null &&
            _tracker.Runner != null &&
            _giverPlayerId >= 0 &&
            _tracker.Runner.LocalPlayer.PlayerId == _giverPlayerId;

        private void HandleGiverGrabbed(int trialId, int playerId, NetworkId objectId)
        {
            _giverPlayerId  = playerId;
            _giverGrabbedAt = DateTime.UtcNow;
        }

        private void HandleReceiverTouched(int trialId, int playerId, NetworkId objectId)
        {
            _receiverTouchedAt = DateTime.UtcNow;
        }

        private void HandleReceiverGrabbed(int trialId, int playerId, NetworkId objectId)
        {
            _receiverPlayerId  = playerId;
            _receiverGrabbedAt = DateTime.UtcNow;
            if (_giverPlayerId < 0)
                Debug.LogWarning("[HandoverReporter] ReceiverGrabbed fired but giverPlayerId not set — GiverGrabbed may have been missed.");
            if (IsGiverClient)
                StartCoroutine(PostHandoverAndPatchTimestamps(trialId));
        }

        private void HandleGiverReleased(int trialId, int playerId, NetworkId objectId)
        {
            if (!IsGiverClient) return;
            if (_activeHandoverId > 0)
                StartCoroutine(PatchGiverReleased(DateTime.UtcNow));
            else
                _pendingGiverReleasedAt = DateTime.UtcNow; // POST still in flight — flush after it completes
        }

        private void HandleObjectDropped()
        {
            if (!IsGiverClient) return;
            if (_activeHandoverId > 0)
                StartCoroutine(PatchDropError());
            else
                _pendingDropError = true; // POST still in flight — flush after it completes
        }

        // ── HTTP coroutines ──────────────────────────────────────────────────────

        private IEnumerator PostHandoverAndPatchTimestamps(int trialId)
        {
            string baseUrl            = _experimentContext != null ? _experimentContext.BackendBaseUrl : "http://localhost:5000";
            // NOTE: GetParticipantId maps Fusion PlayerId → DB participant_id via slot index.
            // This assumes Fusion assigns PlayerId 1/2 matching the backend slot numbers 1/2.
            int    giverParticipantId = _experimentContext != null ? _experimentContext.GetParticipantId(_giverPlayerId)    : -1;
            int    recvParticipantId  = _experimentContext != null ? _experimentContext.GetParticipantId(_receiverPlayerId) : -1;

            // 1. POST /handovers/trials/{trialId}
            string postUrl  = $"{baseUrl}/handovers/trials/{trialId}";
            string postBody = $"{{\"giver\":{giverParticipantId},\"receiver\":{recvParticipantId},\"grasped_object\":\"{gameObject.name}\"}}";

            using var postReq = new UnityWebRequest(postUrl, "POST");
            postReq.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(postBody));
            postReq.downloadHandler = new DownloadHandlerBuffer();
            postReq.SetRequestHeader("Content-Type", "application/json");
            yield return postReq.SendWebRequest();

            if (postReq.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"[HandoverReporter] POST failed: {postReq.error}");
                yield break;
            }

            var parsed = JsonUtility.FromJson<HandoverCreateResponse>(postReq.downloadHandler.text);
            if (parsed == null || parsed.handover_id <= 0)
            {
                Debug.LogError("[HandoverReporter] POST response missing handover_id.");
                yield break;
            }
            _activeHandoverId = parsed.handover_id;

            // 2. PATCH /handovers/{id}/phases — 3 timestamps
            string patchUrl  = $"{baseUrl}/handovers/{_activeHandoverId}/phases";
            string patchBody = $"{{" +
                $"\"giver_grasped_object\":\"{Iso(_giverGrabbedAt)}\"," +
                $"\"receiver_touched_object\":\"{Iso(_receiverTouchedAt)}\"," +
                $"\"receiver_grasped_object\":\"{Iso(_receiverGrabbedAt)}\"" +
                $"}}";

            using var patchReq = new UnityWebRequest(patchUrl, "PATCH");
            patchReq.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(patchBody));
            patchReq.downloadHandler = new DownloadHandlerBuffer();
            patchReq.SetRequestHeader("Content-Type", "application/json");
            yield return patchReq.SendWebRequest();

            if (patchReq.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[HandoverReporter] PATCH timestamps failed: {patchReq.error}");

            // If GiverReleased fired while POST was still in flight, send it now
            if (_pendingGiverReleasedAt.HasValue)
            {
                DateTime ts = _pendingGiverReleasedAt.Value;
                _pendingGiverReleasedAt = null;
                StartCoroutine(PatchGiverReleased(ts));
                yield break; // drop and release are mutually exclusive
            }

            // If object was dropped while POST was still in flight, flag it now
            if (_pendingDropError)
            {
                _pendingDropError = false;
                StartCoroutine(PatchDropError());
            }
        }

        private IEnumerator PatchGiverReleased(DateTime timestamp)
        {
            string baseUrl  = _experimentContext != null ? _experimentContext.BackendBaseUrl : "http://localhost:5000";
            string patchUrl = $"{baseUrl}/handovers/{_activeHandoverId}/phases";
            string body     = $"{{\"giver_released_object\":\"{Iso(timestamp)}\"}}";

            using var req = new UnityWebRequest(patchUrl, "PATCH");
            req.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[HandoverReporter] PATCH GiverReleased failed: {req.error}");

            ResetState();
        }

        private IEnumerator PatchDropError()
        {
            string baseUrl  = _experimentContext != null ? _experimentContext.BackendBaseUrl : "http://localhost:5000";
            string patchUrl = $"{baseUrl}/handovers/{_activeHandoverId}/phases";
            const string body = "{\"is_error\":true,\"error_type\":\"dropped\"}";

            using var req = new UnityWebRequest(patchUrl, "PATCH");
            req.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[HandoverReporter] PATCH DropError failed: {req.error}");

            ResetState();
        }

        // ── Helpers ─────────────────────────────────────────────────────────────

        private void ResetState()
        {
            _activeHandoverId       = -1;
            _giverPlayerId          = -1;
            _receiverPlayerId       = -1;
            _pendingGiverReleasedAt = null;
            _pendingDropError       = false;
            _giverGrabbedAt         = default;
            _receiverTouchedAt      = default;
            _receiverGrabbedAt      = default;
        }

        private static string Iso(DateTime dt) => dt.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");

        [Serializable]
        private class HandoverCreateResponse
        {
            public int handover_id;
        }
    }
}
