using Application.Scripts.Avatar;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public class NetworkRig : NetworkBehaviour
    {
        public const int EXECUTION_ORDER = 100;
        
        public HardwareRig hardwareRig;
        public NetworkHand leftHand;
        public NetworkHand rightHand;
        public NetworkHeadset headset;

        [HideInInspector]
        public NetworkTransform networkTransform;
        
        protected virtual void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
        }

        // As we are in shared topology, having the StateAuthority means we are the local user
        public virtual bool IsLocalNetworkRig => Object && Object.HasStateAuthority;

        public override void Spawned()
        {
            base.Spawned();
            
            if (IsLocalNetworkRig)
            {
                hardwareRig = FindFirstObjectByType<HardwareRig>();
                if (hardwareRig == null) Debug.LogError("Missing HardwareRig in the scene");
            }
        }

        public override void FixedUpdateNetwork()
        {
            base.FixedUpdateNetwork();

            // Update the rig at each network tick for local player. The NetworkTransform will forward this to other players
            if (IsLocalNetworkRig && hardwareRig)
            {
                XRInputState rigState = hardwareRig.RigState;
                ApplyLocalStateToRigParts(rigState);
                ApplyLocalStateToHandPoses(rigState);
            }
        }

        protected virtual void ApplyLocalStateToRigParts(XRInputState rigState)
        {
            transform.position = rigState.PlayArea.Position;
            transform.rotation = rigState.PlayArea.Rotation;
            
            headset.trackingData.SetState(rigState.Head);
            
            leftHand.handTrackingData.wrist.SetPositionAndRotation(rigState.LeftHand.Wrist.Position, rigState.LeftHand.Wrist.Rotation);
            rightHand.handTrackingData.wrist.SetPositionAndRotation(rigState.RightHand.Wrist.Position, rigState.RightHand.Wrist.Rotation);
        }
        
        protected virtual void ApplyLocalStateToHandPoses(XRInputState rigState)
        {
            leftHand.HandState = (HandStateNetworked) rigState.LeftHand;
            rightHand.HandState = (HandStateNetworked) rigState.RightHand;
            // we update the hand pose info. It will trigger on network hands OnHandCommandChange on all clients, and update the hand representation accordingly
            //leftHand.HandCommand = rigState.leftHandCommand;
            //rightHand.HandCommand = rigState.rightHandCommand;
        }

        public override void Render()
        {
            base.Render();
            
            if (IsLocalNetworkRig && hardwareRig != null)
            {
                // Extrapolate for local user :
                // we want to have the visual at the good position as soon as possible, so we force the visuals to follow the most fresh hardware positions

                XRInputState rigState = hardwareRig.RigState;
                ApplyLocalStateToRigParts(rigState);
            }
        }
    }
}