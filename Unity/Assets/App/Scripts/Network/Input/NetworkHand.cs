using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Hardware;
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
        public RigPart Side => side;

        [SerializeField] private Application.Scripts.Avatar.Driver.AvatarDriver avatarDriver;

        /// <summary>
        /// The network-synchronized hand pose state.
        /// Updated on the owner client and replicated to others.
        /// </summary>
        [Networked] public HandStateNetworked HandState { get; set; }

        private NetworkRig _rig;
        private ChangeDetector _changeDetector;

        /// <summary>
        /// Returns true if this hand belongs to the local user (i.e., the local network authority).
        /// </summary>
        public bool IsLocalNetworkRig => _rig.IsLocalNetworkRig;

        /// <summary>
        /// Gets the local hardware hand (e.g., XR controller) that corresponds to this network hand.
        /// Only available if the hand belongs to the local rig.
        /// </summary>
        public HardwareHand LocalHardwareHand => IsLocalNetworkRig ? (side == RigPart.LeftController ? _rig?.hardwareRig?.leftHand : _rig?.hardwareRig?.rightHand)
            : null;

        /// <summary>
        /// The avatar hand bone Transform (wrist). Set by PlayerVisuals after avatar initialization.
        /// Used by NetworkedGrabbable to position grabbed objects relative to the visual hand.
        /// </summary>
        public Transform AvatarHand { get; set; }


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
        /// Called every network tick. Writes the local player's current hand state to the network.
        /// </summary>
        public override void FixedUpdateNetwork()
        {
            base.FixedUpdateNetwork();
            if (!IsLocalNetworkRig) return;

            bool isLeft = side == RigPart.LeftController;
            XRInputState rigState = _rig.hardwareRig.RigState;
            HandState localHandState = isLeft ? rigState.LeftHand : rigState.RightHand;
            HandState = (HandStateNetworked)localHandState;
        }

        /// <summary>
        /// Called every render frame.
        /// For the local user: applies extrapolated hand pose data via AvatarDriver.
        /// For remote users: updates visuals based on received network data via AvatarDriver.
        /// </summary>
        public override void Render()
        {
            base.Render();

            if (avatarDriver == null) return;

            bool isLeft = side == RigPart.LeftController;
            HandState handState;
            TransformState head;

            if (IsLocalNetworkRig)
            {
                XRInputState rigState = _rig.hardwareRig.RigState;
                handState = isLeft ? rigState.LeftHand : rigState.RightHand;
                head = rigState.Head;
            }
            else
            {
                handState = (HandState)HandState;
                head = new TransformState
                {
                    Position = _rig.headset.transform.position,
                    Rotation = _rig.headset.transform.rotation,
                };
            }

            // ApplyHand drives head/body + one side only, preventing the two
            // NetworkHand instances (left/right) from overwriting each other's results.
            avatarDriver.ApplyHand(handState, isLeft, head);
        }
    }
}
