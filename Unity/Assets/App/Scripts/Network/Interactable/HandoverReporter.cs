using System;
using Application.Scripts.Study;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Interactable
{
    /// <summary>
    /// Accumulates handover phase timestamps and delegates reporting to BackendService.
    /// Only the giver-client reports (IsGiverClient guard).
    /// HandoverData is built incrementally across phase events and sent complete on GiverReleased or drop.
    /// </summary>
    public class HandoverReporter : MonoBehaviour
    {
        [SerializeField] private BackendService _backendService;

        private HandoverTracker        _tracker;
        private NetworkGrabbableObject _netGrabbable;

        private int _giverPlayerId    = -1;
        private int _receiverPlayerId = -1;

        private DateTime  _giverGraspedAt;
        private DateTime  _receiverTouchedAt;
        private DateTime  _receiverGraspedAt;
        private SessionState _session;

        private void Awake()
        {
            _tracker      = GetComponent<HandoverTracker>();
            _netGrabbable = GetComponent<NetworkGrabbableObject>();
        }

        private void OnEnable()
        {
            if (_backendService != null)
                _backendService.OnSessionReady.AddListener(OnSessionReady);
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
            if (_backendService != null)
                _backendService.OnSessionReady.RemoveListener(OnSessionReady);
            if (_tracker != null)
            {
                _tracker.OnGiverGrabbedEvent    -= HandleGiverGrabbed;
                _tracker.OnReceiverTouchedEvent -= HandleReceiverTouched;
                _tracker.OnReceiverGrabbedEvent -= HandleReceiverGrabbed;
                _tracker.OnGiverReleasedEvent   -= HandleGiverReleased;
            }
            if (_netGrabbable != null)
                _netGrabbable.onObjectDropped.RemoveListener(HandleObjectDropped);
            ResetState();
        }

        private void OnSessionReady(SessionState session) => _session = session;

        private bool IsGiverClient =>
            _tracker?.Runner != null &&
            _tracker.Runner.IsRunning &&
            _giverPlayerId >= 0 &&
            _tracker.Runner.LocalPlayer.PlayerId == _giverPlayerId;

        private void HandleGiverGrabbed(int trialId, int playerId, NetworkId objectId)
        {
            _giverPlayerId  = playerId;
            _giverGraspedAt = DateTime.UtcNow;
        }

        private void HandleReceiverTouched(int trialId, int playerId, NetworkId objectId)
            => _receiverTouchedAt = DateTime.UtcNow;

        private void HandleReceiverGrabbed(int trialId, int playerId, NetworkId objectId)
        {
            _receiverPlayerId  = playerId;
            _receiverGraspedAt = DateTime.UtcNow;
        }

        private void HandleGiverReleased(int trialId, int playerId, NetworkId objectId)
        {
            if (!IsGiverClient) return;
            _backendService?.ReportHandover(BuildData(isError: false, releasedAt: DateTime.UtcNow));
            ResetState();
        }

        private void HandleObjectDropped()
        {
            if (!IsGiverClient) return;
            _backendService?.ReportHandover(BuildData(isError: true, errorType: "dropped"));
            ResetState();
        }

        private HandoverData BuildData(bool isError, DateTime? releasedAt = null, string errorType = null)
            => new HandoverData
            {
                TrialId               = _session?.TrialId ?? 0,
                GiverParticipantId    = _session?.GetParticipantId(_giverPlayerId)    ?? -1,
                ReceiverParticipantId = _session?.GetParticipantId(_receiverPlayerId) ?? -1,
                GraspedObject         = gameObject.name,
                GiverGraspedAt        = _giverGraspedAt,
                ReceiverTouchedAt     = _receiverTouchedAt,
                ReceiverGraspedAt     = _receiverGraspedAt,
                GiverReleasedAt       = releasedAt,
                IsError               = isError,
                ErrorType             = errorType
            };

        private void ResetState()
        {
            _giverPlayerId     = -1;
            _receiverPlayerId  = -1;
            _giverGraspedAt    = default;
            _receiverTouchedAt = default;
            _receiverGraspedAt = default;
        }
    }
}
