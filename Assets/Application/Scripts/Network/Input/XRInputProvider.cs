using System;
using System.Collections.Generic;
using Application.Scripts.Avatar_rigging;
using Fusion;
using Fusion.Sockets;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    [System.Serializable]
    public class Offsets
    {
        public Vector3 trackingPositionOffset;
        public Vector3 trackingRotationOffset;
    }
    
    /// <summary>
    /// Pools the Input from XR sources like headset or hands and synchronize the input state in network.
    /// For more information see <see cref="https://doc.photonengine.com/fusion/current/manual/data-transfer/player-input"/>
    /// </summary>
    public class XRInputProvider : SimulationBehaviour, INetworkRunnerCallbacks
    {
        [Header("XR References")]
        [SerializeField] private Transform xrRig;
        [SerializeField] private Offsets rigOffsets;
        [SerializeField] private Transform headset;
        [SerializeField] private Offsets headOffsets;

        [SerializeField] private HandTrackingData leftHand;
        [SerializeField] private HandTrackingData rightHand;

        void OnEnable()
        {
            if(Runner != null){
                Runner.AddCallbacks( this );
            }
        }
        
        public void OnDisable(){
            if(Runner != null){
                Runner.RemoveCallbacks( this );
            }
        }
        
        public void OnInput(NetworkRunner runner, NetworkInput input)
        {
            XRInputState xrInputState = new XRInputState
            {
                PlayAreaPosition = xrRig.position,
                PlayAreaRotation = xrRig.rotation,
                
                HeadsetPosition = ProcessPosition(headset, headOffsets.trackingPositionOffset),
                HeadsetRotation = ProcessRotation(headset, headOffsets.trackingRotationOffset),
                
                LeftHand = GetHandState(leftHand),
                RightHand = GetHandState(rightHand)
            };

            input.Set(xrInputState);
        }

        private HandState GetHandState(HandTrackingData hand)
        {
            HandState state = new HandState
            {
                WristPosition = ProcessPosition(hand.wristSource, hand.offsetPosition),
                WristRotation = ProcessRotation(hand.wristSource, hand.offsetRotation),
                
                Thumb = GetFingerState(hand.thumb),
                Index = GetFingerState(hand.index),
                Middle = GetFingerState(hand.middle),
                Ring = GetFingerState(hand.ring),
                Pinky = GetFingerState(hand.pinky)
            };

            return state;
        }

        private FingerState GetFingerState(FingerTrackingData finger)
        {
            FingerState state = new FingerState()
            {
                Proximal = GetPhalanxState(finger.proximal),
                Intermediate = GetPhalanxState(finger.intermediate),
                Distal = GetPhalanxState(finger.distal)
            };

            return state;
        }

        private PhalanxState GetPhalanxState(PhalanxTrackingData phalanx)
        {
            PhalanxState state = new PhalanxState()
            {
                Position = ProcessPosition(phalanx.source, phalanx.offsetPosition),
                Rotation = ProcessRotation(phalanx.source, phalanx.offsetRotation)
            };
            return state;
        }

        private Vector3 ProcessPosition(Transform t, Vector3 position)
        {
            return t.TransformPoint(position);
        }

        private Quaternion ProcessRotation(Transform t, Vector3 rotationAngles)
        {
            return t.rotation * Quaternion.Euler(rotationAngles);
        }
        
        #region ##### Unused Network Callbacks #####
        
        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player) { }
        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player) { }
        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }
        public void OnShutdown(NetworkRunner runner, ShutdownReason shutdownReason) { }
        // ReSharper disable once Unity.IncorrectMethodSignature
        public void OnConnectedToServer(NetworkRunner runner) { }
        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason) { }
        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token) { }
        public void OnConnectFailed(NetworkRunner runner, NetAddress remoteAddress, NetConnectFailedReason reason) { }
        public void OnUserSimulationMessage(NetworkRunner runner, SimulationMessagePtr message) { }
        public void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList) { }
        public void OnCustomAuthenticationResponse(NetworkRunner runner, Dictionary<string, object> data) { }
        public void OnHostMigration(NetworkRunner runner, HostMigrationToken hostMigrationToken) { }
        public void OnReliableDataReceived(NetworkRunner runner, PlayerRef player, ReliableKey key, ArraySegment<byte> data) { }
        public void OnReliableDataProgress(NetworkRunner runner, PlayerRef player, ReliableKey key, float progress) { }
        public void OnSceneLoadDone(NetworkRunner runner) { }
        public void OnSceneLoadStart(NetworkRunner runner) { }
        
        #endregion
    }
}
