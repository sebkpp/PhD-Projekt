using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction.States;
using Application.Scripts.Network.Input.States;
using Application.Scripts.Utils.Extensions;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    /// <summary>
    /// Represents the networked XR rig of a player in a Fusion multiplayer environment.
    /// This component synchronizes the player's headset and hands based on hardware input,
    /// and updates the network transform for remote representation.
    /// </summary>
    /// <remarks>
    /// This class should be attached to the root GameObject of a player's avatar prefab.
    /// It is only active for the local player instance (i.e., the one with <see cref="Object.HasStateAuthority"/>).
    /// On each network tick, it copies the local XR hardware state (e.g. headset, hands) into the networked rig.
    /// </remarks>
    [RequireComponent(typeof(AvatarConfigReference))]
    public class NetworkRig : NetworkBehaviour
    {
        /// <summary>
        /// Recommended execution order value for script execution, to ensure correct timing.
        /// </summary>
        // ReSharper disable once InconsistentNaming
        public const int EXECUTION_ORDER = 100;
        
        /// <summary>
        /// Reference to the local XR hardware rig providing tracking data.
        /// This is only set for the local player.
        /// </summary>
        public HardwareRig hardwareRig;
        
        /// <summary>
        /// Networked representation of the player's left hand.
        /// </summary>
        public NetworkHand leftHand;
        
        /// <summary>
        /// Networked representation of the player's right hand.
        /// </summary>
        public NetworkHand rightHand;
        
        /// <summary>
        /// Networked representation of the player's headset.
        /// </summary>
        public NetworkHeadset headset;

        /// <summary>
        /// NetworkTransform-Fusion component used to sync the player's root transform over the network.
        /// </summary>
        [HideInInspector]
        public NetworkTransform networkTransform;

        [Header("Debug")]
        [SerializeField] private SkinnedMeshRenderer handMesh;
        private static readonly int HandColorProperty = Shader.PropertyToID("_c1");
        private Color _savedHandColor;

        [Networked] public bool DebugMode { get; set; }

        private AvatarConfig _avatarConfig;
        
        /// <summary>
        /// The avatar configuration used by this network rig.
        /// Retrieved from the <see cref="AvatarConfigReference"/> component.
        /// </summary>
        public AvatarConfig AvatarConfig => _avatarConfig;
        
        /// <summary>
        /// Unity Awake method.
        /// Initializes required references such as <see cref="NetworkTransform"/> and <see cref="AvatarConfig"/>.
        /// </summary>
        protected virtual void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            _avatarConfig = GetComponent<AvatarConfigReference>().Config;

            if (_avatarConfig == null)
            {
                Debug.LogWarning($"{nameof(NetworkRig)} on {gameObject.name} has no AvatarConfig assigned!", this);
            }

            if (handMesh != null) _savedHandColor = handMesh.sharedMaterial.GetColor(HandColorProperty);
        }

        /// <summary>
        /// Returns true if this instance belongs to the local player (i.e., has state authority).
        /// </summary>
        public virtual bool IsLocalNetworkRig => Object && Object.HasStateAuthority;

        /// <summary>
        /// Called by Fusion when the networked object is spawned.
        /// Assigns the local hardware rig if this is the local player's rig.
        /// </summary>
        public override void Spawned()
        {
            base.Spawned();

            if (!IsLocalNetworkRig) return;
            
            hardwareRig = FindFirstObjectByType<HardwareRig>();
            if (hardwareRig == null) Debug.LogError("Missing HardwareRig in the scene");
        }

        /// <summary>
        /// Called by Fusion on each network tick.
        /// Updates the rig's transform and parts based on the current local hardware state,
        /// which will then be synchronized to other clients via the <see cref="NetworkTransform"/>.
        /// </summary>
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

        /// <summary>
        /// Applies the current XR hardware state to the rig parts (headset and hands).
        /// Used during both simulation and rendering.
        /// </summary>
        /// <param name="rigState">The XR input state retrieved from the local hardware rig.</param>
        protected virtual void ApplyLocalStateToRigParts(XRInputState rigState)
        {
            transform.position = rigState.PlayArea.Position;
            transform.rotation = rigState.PlayArea.Rotation;
            
            headset.transform.SetTransformState(rigState.Head);
            
            leftHand.HandState = (HandStateNetworked) rigState.LeftHand;
            rightHand.HandState = (HandStateNetworked) rigState.RightHand;
        }

        /// <summary>
        /// Called by Fusion during the render phase.
        /// Applies the latest hardware input state to the visual representation of the rig.
        /// This ensures local visuals are up-to-date and responsive before the next simulation tick.
        /// </summary>
        public override void Render()
        {
            base.Render();

            if (!IsLocalNetworkRig || hardwareRig == null) return;
            
            // Extrapolate for local user :
            // we want to have the visual at the good position as soon as possible, so we force the visuals to follow the most fresh hardware positions
            XRInputState rigState = hardwareRig.RigState;
            ApplyLocalStateToRigParts(rigState);
        }

        /// <summary>
        /// Enables or disables debug visualization on the hand mesh.
        /// In debug mode, the local rig's hand is colored red and remote rigs are colored blue.
        /// </summary>
        /// <param name="enable">True to enable debug coloring, false to restore the original color.</param>
        public void EnableDebug(bool enable)
        {
            DebugMode = enable;
            if (handMesh == null) return;
            Color color = enable
                ? (IsLocalNetworkRig ? Color.red : Color.blue)
                : _savedHandColor;
            handMesh.sharedMaterial.SetColor(HandColorProperty, color);
        }
    }
}