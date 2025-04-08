using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction.States;
using Application.Scripts.Network.Input.States;
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
            }
        }

        protected virtual void ApplyLocalStateToRigParts(XRInputState rigState)
        {
            transform.position = rigState.PlayArea.Position;
            transform.rotation = rigState.PlayArea.Rotation;
            
            headset.transform.SetTransformState(rigState.Head);
            
            leftHand.HandState = (HandStateNetworked) rigState.LeftHand;
            rightHand.HandState = (HandStateNetworked) rigState.RightHand;
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