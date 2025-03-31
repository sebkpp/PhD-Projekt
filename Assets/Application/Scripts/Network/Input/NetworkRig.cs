using System;
using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Utils.Extensions;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    [RequireComponent(typeof(AvatarConfigReference))]
    public class NetworkRig : NetworkBehaviour
    {
        public const int EXECUTION_ORDER = 100;
        
        public HardwareRig hardwareRig;
        public NetworkHand leftHand;
        public NetworkHand rightHand;
        public NetworkHeadset headset;

        [HideInInspector]
        public NetworkTransform networkTransform;
        
        
        private AvatarConfig _avatarConfig;
        public AvatarConfig AvatarConfig => _avatarConfig;
        
        protected virtual void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            _avatarConfig = GetComponent<AvatarConfigReference>().Config;

            if (_avatarConfig == null)
            {
                Debug.LogWarning($"{nameof(NetworkRig)} on {gameObject.name} has no AvatarConfig assigned!", this);
            }
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
                //ApplyLocalStateToHandPoses(rigState);
            }
        }

        protected virtual void ApplyLocalStateToRigParts(XRInputState rigState)
        {
            transform.position = rigState.PlayArea.Position;
            transform.rotation = rigState.PlayArea.Rotation;
            
            headset.transform.SetTransformState(rigState.Head);
            
            // Left/Right Hand
            Transform cachedNetworkLeftHand = leftHand.transform;
            
            Vector3 worldOffset = cachedNetworkLeftHand.rotation * _avatarConfig.LeftHand.wrist.position;
            cachedNetworkLeftHand.position = rigState.LeftHandWrist.Position + worldOffset;
            cachedNetworkLeftHand.rotation = rigState.LeftHandWrist.Rotation * Quaternion.Euler(_avatarConfig.LeftHand.wrist.rotation);

            Transform cachedNetworkRightHand = rightHand.transform;
            
            worldOffset = cachedNetworkRightHand.rotation * _avatarConfig.RightHand.wrist.position;
            cachedNetworkRightHand.position = rigState.RightHandWrist.Position + worldOffset;
            cachedNetworkRightHand.rotation = rigState.RightHandWrist.Rotation * Quaternion.Euler(_avatarConfig.RightHand.wrist.rotation);
            
            leftHand.handTrackingData.SetHandPose(rigState.LeftHand, _avatarConfig.LeftHand);
            rightHand.handTrackingData.SetHandPose(rigState.RightHand, _avatarConfig.RightHand);
        }
        
        protected virtual void ApplyLocalStateToHandPoses(XRInputState rigState)
        {
            XRInputState state = rigState;

            //state.LeftHand.ApplyHandPoseOffset(_avatarConfig.LeftHand);
            
            leftHand.HandState = (HandStateNetworked) state.LeftHand;
            rightHand.HandState = (HandStateNetworked) state.RightHand;

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