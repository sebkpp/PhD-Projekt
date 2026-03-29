using Application.Scripts.Avatar.Grab;
using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using Fusion;
using Fusion.Addons.Physics;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Network.Interactable
{
    /// <summary>
    /// Networked grab component. Manages spring-physics dual-grip, authority transfer,
    /// and visual hand blending during a hand-to-hand object handover.
    /// Replaces the old NetworkedGrabbable single-grab system.
    /// </summary>
    public class NetworkGrabbableObject : NetworkBehaviour
    {
        [HideInInspector] public NetworkTransform   networkTransform;
        [HideInInspector] public NetworkRigidbody3D networkRigidbody;
        [HideInInspector] public Grabbable          grabbable;

        [SerializeField] private GrabSettings _settings;

        [Networked] public NetworkBool       InitialIsKinematicState { get; set; }
        [Networked] public NetworkedGrabber  GiverGrabber            { get; set; }
        [Networked] public NetworkedGrabber  ReceiverGrabber         { get; set; }

        public bool IsGrabbed => Object != null && GiverGrabber != null;

        [Header("Events")]
        public UnityEvent<NetworkedGrabber> onDidGrab   = new();
        public UnityEvent                   onDidUngrab = new();

        [Header("Advanced")]
        public bool extrapolateWhileTakingAuthority = true;
        public bool isTakingAuthority;

        private ChangeDetector _funChangeDetector;
        private ChangeDetector _renderChangeDetector;

        // Local grab state (not networked — only valid on this client)
        private GrabHand _localGrabHand;

        private void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            networkRigidbody = GetComponent<NetworkRigidbody3D>();
            grabbable        = GetComponent<Grabbable>();
            if (grabbable == null)
            {
                Debug.LogError("[NetworkGrabbableObject] Requires a Grabbable component.");
                grabbable = gameObject.AddComponent<Grabbable>();
            }
        }

        public override void Spawned()
        {
            base.Spawned();
            if (Object.HasStateAuthority && grabbable.rb != null)
                InitialIsKinematicState = grabbable.rb.isKinematic;

            grabbable.expectedIsKinematic = InitialIsKinematicState;
            _funChangeDetector    = GetChangeDetector(ChangeDetector.Source.SimulationState);
            _renderChangeDetector = GetChangeDetector(ChangeDetector.Source.SnapshotFrom);
        }

        public override void FixedUpdateNetwork()
        {
            // Detect and apply physics state changes
            if (TryDetectGrabberChange(_funChangeDetector, out var prevGiver, out var curGiver))
            {
                if (prevGiver != null && curGiver == null && ReceiverGrabber == null)
                    grabbable.UnlockObjectPhysics();
                if (curGiver != null)
                    grabbable.LockObjectPhysics();
            }

            if (!IsGrabbed || !Object.HasStateAuthority) return;

            float giverGrip    = GiverGrabber    != null ? GiverGrabber.EffectiveGrip    : 0f;
            float receiverGrip = ReceiverGrabber != null ? ReceiverGrabber.EffectiveGrip : 0f;
            float totalGrip    = giverGrip + receiverGrip;

            float dropThreshold = _settings != null ? _settings.dropThreshold : 0.4f;
            if (totalGrip < dropThreshold)
            {
                // Nobody has a sufficient grip — let it fall
                grabbable.UnlockObjectPhysics();
                GiverGrabber    = null;
                ReceiverGrabber = null;
                return;
            }

            ApplySpringForces(giverGrip, receiverGrip);
            CheckAuthorityTransfer(giverGrip);
        }

        private void ApplySpringForces(float giverGrip, float receiverGrip)
        {
            if (grabbable.rb == null) return;

            float k       = _settings != null ? _settings.springConstant : 800f;
            float damping = _settings != null ? _settings.damping        : 12f;

            Vector3 force = Vector3.zero;
            Vector3 pos   = transform.position;

            if (GiverGrabber != null)
                force += (GiverGrabber.HandPosition - pos) * giverGrip * k;

            if (ReceiverGrabber != null)
                force += (ReceiverGrabber.HandPosition - pos) * receiverGrip * k;

            force -= grabbable.rb.linearVelocity * damping;
            grabbable.rb.AddForce(force, ForceMode.Force);
        }

        private void CheckAuthorityTransfer(float giverGrip)
        {
            float releaseThreshold = _settings != null ? _settings.releaseThreshold : 0.3f;
            if (ReceiverGrabber != null && giverGrip < releaseThreshold)
            {
                // Giver released — receiver becomes new giver
                GiverGrabber    = ReceiverGrabber;
                ReceiverGrabber = null;
                TransferAuthorityToNewGiver();
            }
        }

        private async void TransferAuthorityToNewGiver()
        {
            isTakingAuthority = true;
            await Object.WaitForStateAuthority();
            isTakingAuthority = false;
        }

        public override void Render()
        {
            if (TryDetectGrabberChange(_renderChangeDetector, out var prev, out var cur))
            {
                if (prev != null) onDidUngrab?.Invoke();
                if (cur  != null) onDidGrab?.Invoke(cur);
            }

            if (isTakingAuthority && extrapolateWhileTakingAuthority)
            {
                ExtrapolateWhileTakingAuthority();
                return;
            }

            if (!IsGrabbed || !Object.HasStateAuthority) return;

            // Blend visual hand position toward object based on tension
            BlendHandVisuals();
        }

        private void BlendHandVisuals()
        {
            if (_localGrabHand == null || _settings == null) return;

            float distance    = Vector3.Distance(_localGrabHand.transform.position, transform.position);
            float tension     = Mathf.Clamp01(distance / _settings.maxGripReach);
            float blendWeight = tension * _settings.maxHandBlend;

            // Offset the rendered hand position toward the object
            Vector3 trackedPos  = _localGrabHand.transform.position;
            Vector3 blendedPos  = Vector3.Lerp(trackedPos, transform.position, blendWeight);
            _localGrabHand.transform.position = blendedPos;
        }

        private void ExtrapolateWhileTakingAuthority()
        {
            if (_localGrabHand == null) return;
            // Keep visual representation following the local hand while waiting for authority
        }

        #region Local grab API (called by GrabHand)

        public void LocalGrab(GrabHand grabHand)
        {
            _localGrabHand = grabHand;
            if (GiverGrabber == null)
            {
                // First grabber becomes the giver
                RequestGiverGrab(grabHand.networkGrabber);
            }
            else
            {
                // Second grabber becomes the receiver (dual-grip)
                ReceiverGrabber = grabHand.networkGrabber;
                // Notify HandoverTracker — receiver's first contact is when they initiate grab
                GetComponent<HandoverTracker>()?.OnReceiverFirstContact(
                    grabHand.networkGrabber.Object.InputAuthority.PlayerId);
            }
        }

        private async void RequestGiverGrab(NetworkedGrabber grabber)
        {
            isTakingAuthority = true;
            await Object.WaitForStateAuthority();
            isTakingAuthority = false;

            if (_localGrabHand == null) return; // ungrabbed before authority arrived
            GiverGrabber = grabber;
            grabbable.LockObjectPhysics();
        }

        public void LocalUngrab(GrabHand grabHand)
        {
            if (_localGrabHand == grabHand)
                _localGrabHand = null;

            if (GiverGrabber != null && GiverGrabber == grabHand.networkGrabber)
            {
                GiverGrabber = ReceiverGrabber; // promote receiver if any
                ReceiverGrabber = null;
                if (GiverGrabber == null)
                    grabbable.UnlockObjectPhysics();
            }
            else if (ReceiverGrabber != null && ReceiverGrabber == grabHand.networkGrabber)
            {
                ReceiverGrabber = null;
            }
        }

        #endregion

        private bool TryDetectGrabberChange(ChangeDetector detector,
            out NetworkedGrabber prev, out NetworkedGrabber cur)
        {
            prev = null; cur = null;
            foreach (var name in detector.DetectChanges(this, out var previous, out var current))
            {
                if (name == nameof(GiverGrabber))
                {
                    var reader = GetBehaviourReader<NetworkedGrabber>(name);
                    prev = reader.Read(previous);
                    cur  = reader.Read(current);
                    return true;
                }
            }
            return false;
        }
    }
}
