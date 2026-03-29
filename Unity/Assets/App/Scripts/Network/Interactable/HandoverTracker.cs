using Application.Scripts.Network.Interaction;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Interactable
{
    /// <summary>
    /// Fires the four study events for a handover interaction:
    /// GiverGrabbed -> ReceiverTouched -> ReceiverGrabbed -> GiverReleased.
    ///
    /// Attach to the same GameObject as NetworkGrabbableObject.
    /// Events are broadcast to all clients via Fusion RPC.
    /// Each payload: trialId, timestamp, playerId, objectNetworkId.
    /// </summary>
    public class HandoverTracker : NetworkBehaviour
    {
        private NetworkGrabbableObject _netGrabbable;
        private int _trialId; // set externally by ExperimentContext or scene setup

        // Tracks current phase to prevent duplicate event firing
        private bool _giverGrabbedFired;
        private bool _receiverTouchedFired;
        private bool _receiverGrabbedFired;

        public void SetTrialId(int trialId) => _trialId = trialId;

        private void Awake()
        {
            _netGrabbable = GetComponent<NetworkGrabbableObject>();
            if (_netGrabbable == null)
                Debug.LogError("[HandoverTracker] Requires NetworkGrabbableObject on the same GameObject.");
        }

        private void OnEnable()
        {
            if (_netGrabbable == null) return;
            _netGrabbable.onDidGrab.AddListener(OnDidGrab);
            _netGrabbable.onDidUngrab.AddListener(OnDidUngrab);
        }

        private void OnDisable()
        {
            if (_netGrabbable == null) return;
            _netGrabbable.onDidGrab.RemoveListener(OnDidGrab);
            _netGrabbable.onDidUngrab.RemoveListener(OnDidUngrab);
        }

        private void OnDidGrab(NetworkedGrabber grabber)
        {
            if (!_giverGrabbedFired)
            {
                // First grab = giver grabbed
                _giverGrabbedFired = true;
                _receiverGrabbedFired = false;
                _receiverTouchedFired = false;
                int playerId = grabber.Object.InputAuthority.PlayerId;
                RPC_FireGiverGrabbed(_trialId, Runner.SimulationTime, playerId, Object.Id);
            }
            else if (_giverGrabbedFired && !_receiverGrabbedFired)
            {
                // Second grab while giver still holds = receiver grabbed
                _receiverGrabbedFired = true;
                int playerId = grabber.Object.InputAuthority.PlayerId;
                RPC_FireReceiverGrabbed(_trialId, Runner.SimulationTime, playerId, Object.Id);
            }
        }

        private void OnDidUngrab()
        {
            if (_receiverGrabbedFired && _giverGrabbedFired)
            {
                // Giver released after receiver had grabbed
                int playerId = _netGrabbable.GiverGrabber != null
                    ? _netGrabbable.GiverGrabber.Object.InputAuthority.PlayerId
                    : 0;
                RPC_FireGiverReleased(_trialId, Runner.SimulationTime, playerId, Object.Id);
                ResetPhase();
            }
            else
            {
                ResetPhase();
            }
        }

        /// <summary>
        /// Called by NetworkGrabbableObject.LocalGrab when the first fingertip of a second hand touches the object.
        /// </summary>
        public void OnReceiverFirstContact(int receiverPlayerId)
        {
            if (_giverGrabbedFired && !_receiverTouchedFired)
            {
                _receiverTouchedFired = true;
                RPC_FireReceiverTouched(_trialId, Runner.SimulationTime, receiverPlayerId, Object.Id);
            }
        }

        private void ResetPhase()
        {
            _giverGrabbedFired    = false;
            _receiverTouchedFired = false;
            _receiverGrabbedFired = false;
        }

        [Rpc(RpcSources.StateAuthority, RpcTargets.All)]
        private void RPC_FireGiverGrabbed(int trialId, float timestamp, int playerId, NetworkId objectId)
            => Debug.Log($"[Handover] GiverGrabbed trial={trialId} t={timestamp:F3} player={playerId} obj={objectId}");

        [Rpc(RpcSources.StateAuthority, RpcTargets.All)]
        private void RPC_FireReceiverTouched(int trialId, float timestamp, int playerId, NetworkId objectId)
            => Debug.Log($"[Handover] ReceiverTouched trial={trialId} t={timestamp:F3} player={playerId} obj={objectId}");

        [Rpc(RpcSources.StateAuthority, RpcTargets.All)]
        private void RPC_FireReceiverGrabbed(int trialId, float timestamp, int playerId, NetworkId objectId)
            => Debug.Log($"[Handover] ReceiverGrabbed trial={trialId} t={timestamp:F3} player={playerId} obj={objectId}");

        [Rpc(RpcSources.StateAuthority, RpcTargets.All)]
        private void RPC_FireGiverReleased(int trialId, float timestamp, int playerId, NetworkId objectId)
            => Debug.Log($"[Handover] GiverReleased trial={trialId} t={timestamp:F3} player={playerId} obj={objectId}");
    }
}
