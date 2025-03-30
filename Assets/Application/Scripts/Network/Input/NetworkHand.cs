using Application.Scripts.Avatar_rigging;
using Application.Scripts.Avatar;
using Fusion;
using UnityEngine;
using UnityEngine.Serialization;

namespace Application.Scripts.Network.Input
{
    public interface IHandRepresentation
    {
        public GameObject gameObject { get; }
        public void SetHandColor(Color color);
        public void SetHandMaterial(Material material);
        public void DisplayMesh(bool shouldDisplay);
        public bool IsMeshDisplayed { get; }
    }

    [RequireComponent(typeof(NetworkTransform))]
    public class NetworkHand : NetworkBehaviour
    {
        public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;
        [HideInInspector] public NetworkTransform networkTransform;
        [SerializeField] private RigPart side;
        [SerializeField] public HandRig handTrackingData;

        [Networked] public HandStateNetworked HandState { get; set; }
        
        
        private NetworkRig _rig;
        private IHandRepresentation _handRepresentation;
        private ChangeDetector _changeDetector;

        public bool IsLocalNetworkRig => _rig.IsLocalNetworkRig;

        public HardwareHand LocalHardwareHand => IsLocalNetworkRig ? (side == RigPart.LeftController ? _rig?.hardwareRig?.leftHand : _rig?.hardwareRig?.rightHand)
            : null;
        private void Awake()
        {
            _rig = GetComponentInParent<NetworkRig>();
            networkTransform = GetComponent<NetworkTransform>();
            _handRepresentation = GetComponentInChildren<IHandRepresentation>();
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
                // Extrapolate for local user : we want to have the visual at the good position as soon as possible, so we force the visuals to follow the most fresh hand pose
                handTrackingData.HandState = LocalHardwareHand.HandTrackingData.GetHandState();
            }
            else
            {
                foreach (var changedNetworkedVarName in _changeDetector.DetectChanges(this))
                {
                    if (changedNetworkedVarName == nameof(HandState))
                    {
                        // Will be called when the local user change the hand pose structure
                        // We trigger here the actual animation update
                        handTrackingData.HandState= HandState;
                    }
                }
            }
        }
    }
}