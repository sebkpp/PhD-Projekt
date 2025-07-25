using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction.States;
using Application.Scripts.Network.Input.States;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    /// <summary>
    /// Synchronizes and applies hand pose data (local and remote) in a networked multiplayer context.
    /// Handles pose replication, change detection, and visual extrapolation for immersive hand presence.
    /// </summary>
    public class NetworkHand : NetworkBehaviour
    {
        /// <summary>
        /// Execution order constant used to determine script update order relative to other components.
        /// </summary>
        // ReSharper disable once InconsistentNaming
        public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;
        
        
        [SerializeField] private RigPart side;
        
        /// <summary>
        /// Reference to the hand tracking data component that applies visual hand poses.
        /// </summary>
        [SerializeField] public HandTrackingData handTrackingData;

        [SerializeField] private Transform avatarHand;
        
        /// <summary>
        /// The network-synchronized hand pose state.
        /// Updated on the owner client and replicated to others.
        /// </summary>
        [Networked] public HandStateNetworked HandState { get; set; }
        
        private NetworkRig _rig;
        private ChangeDetector _changeDetector;
        private HandOffsets _offsetsConfig;

        /// <summary>
        /// Returns true if this hand belongs to the local user (i.e., the local network authority).
        /// </summary>
        public bool IsLocalNetworkRig => _rig.IsLocalNetworkRig;
        
        /// <summary>
        /// Gets the transform of the avatar's visual hand representation.
        /// </summary>
        public Transform AvatarHand => avatarHand;
        
        /// <summary>
        /// Gets the local hardware hand (e.g., XR controller) that corresponds to this network hand.
        /// Only available if the hand belongs to the local rig.
        /// </summary>
        public HardwareHand LocalHardwareHand => IsLocalNetworkRig ? (side == RigPart.LeftController ? _rig?.hardwareRig?.leftHand : _rig?.hardwareRig?.rightHand)
            : null;
        
        
        private void Awake()
        {
            _rig = GetComponentInParent<NetworkRig>();
        }

        /// <summary>
        /// Called when the networked object has been spawned.
        /// Initializes change detection for tracking replicated property updates.
        /// </summary>
        public override void Spawned()
        {
            base.Spawned();
            _changeDetector = GetChangeDetector(ChangeDetector.Source.SnapshotFrom);
        }

        /// <summary>
        /// Called every render frame.
        /// For the local user: applies extrapolated hand pose data.
        /// For remote users: updates visuals based on received network data.
        /// </summary>
        public override void Render()
        {
            base.Render();
            if (IsLocalNetworkRig)
            {
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
                    if (changedNetworkedVarName != nameof(HandState)) continue;
                    
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