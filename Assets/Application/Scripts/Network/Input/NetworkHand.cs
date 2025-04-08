using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction.States;
using Application.Scripts.Network.Input.States;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{

    public class NetworkHand : NetworkBehaviour
    {
        public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;
        [SerializeField] private RigPart side;
        [SerializeField] public HandTrackingData handTrackingData;

        [Networked] public HandStateNetworked HandState { get; set; }
        
        private NetworkRig _rig;
        private ChangeDetector _changeDetector;
        private HandOffsets _offsetsConfig;

        public bool IsLocalNetworkRig => _rig.IsLocalNetworkRig;

        public HardwareHand LocalHardwareHand => IsLocalNetworkRig ? (side == RigPart.LeftController ? _rig?.hardwareRig?.leftHand : _rig?.hardwareRig?.rightHand)
            : null;
        private void Awake()
        {
            _rig = GetComponentInParent<NetworkRig>();
        }

        public override void Spawned()
        {
            base.Spawned();
            _changeDetector = GetChangeDetector(ChangeDetector.Source.SnapshotFrom);
        }

        public override void Render()
        {
            base.Render();
            if (IsLocalNetworkRig)
            {
                //Debug.Log(LocalHardwareHand.HandTrackingData.GetHandPose().Index.Distal.Position);
                // Extrapolate for local user : we want to have the visual at the good position as soon as possible, so we force the visuals to follow the most fresh hand pose
                
                HandState handPose = LocalHardwareHand.HandTrackingData.GetHandPose();
                
                _offsetsConfig = side == RigPart.LeftController
                    ? _rig.AvatarConfig.LeftHand
                    : _rig.AvatarConfig.RightHand;
                
                handTrackingData.SetHandPose(handPose, _offsetsConfig);
                
            }
            else
            {
                foreach (var changedNetworkedVarName in _changeDetector.DetectChanges(this))
                {
                    if (changedNetworkedVarName == nameof(HandState))
                    {
                        // Will be called when the local user change the hand pose structure
                        // We trigger here the actual animation update
                        
                        HandState handPose = HandState;
                        _offsetsConfig = side == RigPart.LeftController
                             ? _rig.AvatarConfig.LeftHand
                             : _rig.AvatarConfig.RightHand;
                        
                        handTrackingData.SetHandPose(handPose, _offsetsConfig);
                    }
                }
            }
        }
    }
}