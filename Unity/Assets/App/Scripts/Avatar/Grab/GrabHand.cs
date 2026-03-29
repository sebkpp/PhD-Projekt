using Application.Scripts.Avatar.Data;
using Application.Scripts.Avatar.Hardware;
using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Network.Interactable;
using UnityEngine;
using UnityEngine.XR.Hands;

namespace Application.Scripts.Avatar.Grab
{
    /// <summary>
    /// Drives grab detection for one hand using XR joint data.
    /// Creates 5 fingertip sphere colliders, counts contact with Grabbable objects,
    /// computes effectiveGrip, and drives NetworkedGrabber networked state.
    /// Lives on the same GameObject as HardwareHand.
    /// </summary>
    [RequireComponent(typeof(HardwareHand))]
    [RequireComponent(typeof(GripStrengthCalculator))]
    public class GrabHand : MonoBehaviour
    {
        [SerializeField] private GrabSettings _settings;

        /// <summary>Current effective grip: fingerCurl x contactFactor x distanceFactor.</summary>
        public float EffectiveGrip { get; private set; }

        /// <summary>The object currently being grabbed (or null).</summary>
        public NetworkGrabbableObject HeldObject { get; private set; }

        // Set by NetworkedGrabber.Spawned() after network spawn
        [HideInInspector] public NetworkedGrabber networkGrabber;

        private HardwareHand _hardwareHand;
        private GripStrengthCalculator _gripCalc;
        private Transform[] _fingertips;   // 5 child transforms, one per finger tip
        private SphereCollider[] _fingertipColliders;
        private Grabbable _candidateGrabbable; // object currently in contact
        private bool _isGrabbing;

        // XRHandJointID for each fingertip, in finger order
        private static readonly XRHandJointID[] TipJoints =
        {
            XRHandJointID.ThumbTip,
            XRHandJointID.IndexTip,
            XRHandJointID.MiddleTip,
            XRHandJointID.RingTip,
            XRHandJointID.LittleTip,
        };

        private void Awake()
        {
            _hardwareHand = GetComponent<HardwareHand>();
            _gripCalc     = GetComponent<GripStrengthCalculator>();

            // Create 5 fingertip child objects with trigger sphere colliders
            _fingertips         = new Transform[5];
            _fingertipColliders = new SphereCollider[5];

            for (int i = 0; i < 5; i++)
            {
                var go = new GameObject($"Fingertip_{i}");
                go.transform.SetParent(transform);
                go.layer = gameObject.layer;

                var col = go.AddComponent<SphereCollider>();
                col.isTrigger = true;
                col.radius    = _settings != null ? _settings.fingertipRadius : 0.012f;

                var reporter = go.AddComponent<FingertipContactReporter>();
                reporter.Owner = this;

                _fingertips[i]         = go.transform;
                _fingertipColliders[i] = col;
            }
        }

        private void Update()
        {
            UpdateFingertipPositions();
            ComputeAndWriteGrip();
            CheckGrabThresholds();
        }

        private void UpdateFingertipPositions()
        {
            if (!_hardwareHand.CurrentPose.IsTracked) return;
            HandPoseData pose = _hardwareHand.CurrentPose;
            for (int i = 0; i < 5; i++)
            {
                HandJointPose tip = pose.GetJoint(TipJoints[i]);
                if (tip.IsValid)
                    _fingertips[i].position = tip.Position;
            }
        }

        private void ComputeAndWriteGrip()
        {
            float rawGrip = _gripCalc.GripStrength;
            float contactFactor = _candidateGrabbable != null
                ? (float)_candidateGrabbable.GetContactCount(this) / 5f
                : 0f;

            float distance = HeldObject != null
                ? Vector3.Distance(transform.position, HeldObject.transform.position)
                : 0f;
            float distanceFactor = _settings != null
                ? Mathf.Clamp01(1f - distance / _settings.maxGripReach)
                : 1f;

            // When grabbing, effective grip uses distance factor. Before grab, it uses contact.
            EffectiveGrip = _isGrabbing
                ? rawGrip * distanceFactor
                : rawGrip * contactFactor;

            // Write to network (NetworkedGrabber set by Spawned)
            if (networkGrabber != null && networkGrabber.Object != null)
            {
                networkGrabber.EffectiveGrip  = EffectiveGrip;
                networkGrabber.HandPosition   = transform.position;
            }

            _hardwareHand.IsGrabbing = _isGrabbing;
        }

        private void CheckGrabThresholds()
        {
            if (_settings == null) return;

            if (!_isGrabbing && EffectiveGrip >= _settings.grabThreshold && _candidateGrabbable != null)
            {
                TryGrab(_candidateGrabbable);
            }
            else if (_isGrabbing && EffectiveGrip < _settings.releaseThreshold)
            {
                TryUngrab();
            }
        }

        private void TryGrab(Grabbable grabbable)
        {
            NetworkGrabbableObject netGrabbable = grabbable.networkGrabbable;
            if (netGrabbable == null) return;

            _isGrabbing = true;
            HeldObject  = netGrabbable;
            netGrabbable.LocalGrab(this);
            grabbable.onGrab?.Invoke();
        }

        private void TryUngrab()
        {
            if (HeldObject == null) return;
            HeldObject.LocalUngrab(this);
            HeldObject.grabbable?.onUngrab?.Invoke();
            _candidateGrabbable?.ClearContacts(this);
            HeldObject  = null;
            _isGrabbing = false;
        }

        /// <summary>Called by FingertipContactReporter when a fingertip enters/exits a Grabbable trigger.</summary>
        public void OnFingertipContact(Grabbable grabbable, bool entering)
        {
            grabbable.RegisterContact(this, entering);

            if (entering && _candidateGrabbable == null && !_isGrabbing)
                _candidateGrabbable = grabbable;

            if (!entering && _candidateGrabbable == grabbable && grabbable.GetContactCount(this) == 0)
                _candidateGrabbable = null;
        }
    }

    /// <summary>
    /// Helper MonoBehaviour on each fingertip child object.
    /// Relays trigger events to the parent GrabHand.
    /// </summary>
    internal class FingertipContactReporter : MonoBehaviour
    {
        public GrabHand Owner;

        private void OnTriggerEnter(Collider other)
        {
            var grabbable = other.GetComponentInParent<Grabbable>();
            if (grabbable != null) Owner.OnFingertipContact(grabbable, entering: true);
        }

        private void OnTriggerExit(Collider other)
        {
            var grabbable = other.GetComponentInParent<Grabbable>();
            if (grabbable != null) Owner.OnFingertipContact(grabbable, entering: false);
        }
    }
}
