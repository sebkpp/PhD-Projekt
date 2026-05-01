using System.Collections.Generic;
using Application.Scripts.Avatar;
using Application.Scripts.Feedback.Auditory;
using Application.Scripts.Feedback.Data;
using Application.Scripts.Feedback.Visual;
using Application.Scripts.Network.Interactable;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Study;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Feedback
{
    /// <summary>
    /// Scene-level orchestrator that wires HandoverTracker events to visual and auditory
    /// feedback providers. Reads slot/stimuli data from SessionState via BackendService.OnSessionReady.
    /// Attach to the FeedbackManager prefab together with BackendService.
    /// </summary>
    public class HandoverFeedbackController : MonoBehaviour
    {
        [SerializeField] private BackendService _backendService;

        private SessionState           _session;
        private HandoverTracker        _tracker;
        private NetworkGrabbableObject _netGrabbable;

        private readonly List<IVisualFeedbackProvider>    _activeVisuals = new();
        private readonly List<IAuditoryFeedbackProvider>  _activeAudio   = new();
        private NetworkedGrabber _giverGrabber;
        private NetworkedGrabber _receiverGrabber;

        private readonly Dictionary<int, HandRenderingController> _renderingControllerCache = new();

        private void Awake()
        {
            _tracker      = FindFirstObjectByType<HandoverTracker>();
            _netGrabbable = FindFirstObjectByType<NetworkGrabbableObject>();
        }

        private void OnEnable()
        {
            if (_backendService != null)
                _backendService.OnSessionReady.AddListener(OnSessionReady);
            if (_tracker != null)
            {
                _tracker.OnGiverGrabbedEvent    += HandleGiverGrabbed;
                _tracker.OnReceiverGrabbedEvent += HandleReceiverGrabbed;
                _tracker.OnGiverReleasedEvent   += HandleGiverReleased;
            }
            if (_netGrabbable != null)
                _netGrabbable.onObjectDropped.AddListener(DeactivateAll);
        }

        private void OnDisable()
        {
            if (_backendService != null)
                _backendService.OnSessionReady.RemoveListener(OnSessionReady);
            if (_tracker != null)
            {
                _tracker.OnGiverGrabbedEvent    -= HandleGiverGrabbed;
                _tracker.OnReceiverGrabbedEvent -= HandleReceiverGrabbed;
                _tracker.OnGiverReleasedEvent   -= HandleGiverReleased;
            }
            if (_netGrabbable != null)
                _netGrabbable.onObjectDropped.RemoveListener(DeactivateAll);
            DeactivateAll();
        }

        private void OnSessionReady(SessionState session)
        {
            _session = session;
        }

        private void Update()
        {
            float giverGrip    = _giverGrabber    != null ? _giverGrabber.EffectiveGrip    : 0f;
            float receiverGrip = _receiverGrabber != null ? _receiverGrabber.EffectiveGrip : 0f;
            foreach (var v in _activeVisuals) v.UpdateGrip(giverGrip, receiverGrip);
            foreach (var a in _activeAudio)   a.UpdateGrip(giverGrip);
        }

        private void HandleGiverGrabbed(int trialId, int giverPlayerId, NetworkId objectId)
        {
            int slot   = _session?.GetSlot(giverPlayerId) ?? giverPlayerId;
            var config = _session?.GetStimuli(slot);
            if (config == null) return;

            bool isLeft = ResolveGrabbingHandIsLeft(_netGrabbable?.GiverGrabber);
            ActivateVisualFor(giverPlayerId, config, isLeft);
            if (IsLocalPlayer(giverPlayerId)) ActivateAudioFor(giverPlayerId, config);
            _giverGrabber = _netGrabbable?.GiverGrabber;
        }

        private void HandleReceiverGrabbed(int trialId, int receiverPlayerId, NetworkId objectId)
        {
            int slot   = _session?.GetSlot(receiverPlayerId) ?? receiverPlayerId;
            var config = _session?.GetStimuli(slot);
            if (config == null) return;

            bool isLeft = ResolveGrabbingHandIsLeft(_netGrabbable?.ReceiverGrabber);
            ActivateVisualFor(receiverPlayerId, config, isLeft);
            if (IsLocalPlayer(receiverPlayerId)) ActivateAudioFor(receiverPlayerId, config);
            _receiverGrabber = _netGrabbable?.ReceiverGrabber;
        }

        private void HandleGiverReleased(int trialId, int playerId, NetworkId objectId)
            => DeactivateAll();

        private void ActivateVisualFor(int playerId, StimulusSlotConfig config, bool isLeft)
        {
            var visualFeedback = GetVisualFeedback(playerId);
            if (visualFeedback == null || config.stimuli == null) return;
            foreach (var s in config.stimuli)
            {
                if (s.stimulus?.stimulus_type == "visual")
                {
                    visualFeedback.Activate(s, _netGrabbable, isLeft);
                    _activeVisuals.Add(visualFeedback);
                    return;
                }
            }
        }

        private void ActivateAudioFor(int playerId, StimulusSlotConfig config)
        {
            var audioProvider = GetAudioProvider(playerId);
            if (audioProvider == null || config.stimuli == null) return;
            foreach (var s in config.stimuli)
            {
                if (s.stimulus?.stimulus_type == "auditory"
                    && s.stimulus.auditives != null
                    && s.stimulus.auditives.Length > 0)
                {
                    audioProvider.Activate(s.stimulus.auditives[0]);
                    _activeAudio.Add(audioProvider);
                    return;
                }
            }
        }

        private void DeactivateAll()
        {
            foreach (var v in _activeVisuals) v.Deactivate();
            _activeVisuals.Clear();
            foreach (var a in _activeAudio) a.Deactivate();
            _activeAudio.Clear();
            _giverGrabber    = null;
            _receiverGrabber = null;
        }

        private bool IsLocalPlayer(int playerId)
            => _tracker?.Runner != null && _tracker.Runner.IsRunning
               && _tracker.Runner.LocalPlayer.PlayerId == playerId;

        private HandRenderingController GetRenderingController(int playerId)
        {
            if (!_renderingControllerCache.TryGetValue(playerId, out var ctrl) || ctrl == null)
            {
                foreach (var c in FindObjectsByType<HandRenderingController>(FindObjectsSortMode.None))
                {
                    if (c.PlayerId == playerId)
                    {
                        _renderingControllerCache[playerId] = c;
                        return c;
                    }
                }
                return null;
            }
            return ctrl;
        }

        private HandVisualFeedback GetVisualFeedback(int playerId)
        {
            var ctrl = GetRenderingController(playerId);
            return ctrl != null ? ctrl.GetComponent<HandVisualFeedback>() : null;
        }

        private IAuditoryFeedbackProvider GetAudioProvider(int playerId)
        {
            var ctrl = GetRenderingController(playerId);
            return ctrl != null ? ctrl.GetComponent<ToneAuditoryFeedback>() : null;
        }

        private static bool ResolveGrabbingHandIsLeft(NetworkedGrabber grabber)
            => grabber != null && grabber.hand != null && grabber.hand.Side == RigPart.LeftController;
    }
}
