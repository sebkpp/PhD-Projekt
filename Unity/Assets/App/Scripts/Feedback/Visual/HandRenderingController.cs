using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Visuals;
using Application.Scripts.Avatar.Grab;
using Application.Scripts.Network.Input;
using UnityEngine;

namespace Application.Scripts.Feedback.Visual
{
    /// <summary>
    /// Manages IH/OH rendering mode for one player's avatar.
    /// In OH mode: LateUpdate overrides the wrist bone position after AvatarDriver drives it,
    /// using Physics.ComputePenetration against the held object's collider with avatar finger bones.
    /// Runs on ALL clients for ALL players, using already-networked HandState bone positions.
    /// </summary>
    public class HandRenderingController : MonoBehaviour
    {
        [SerializeField] private PlayerVisuals _playerVisuals;
        [SerializeField] private GrabSettings _grabSettings;

        private NetworkRig _networkRig;
        private AvatarBoneReference _boneRef;

        // Per-side state
        private HandRenderingMode _leftMode  = HandRenderingMode.IH;
        private HandRenderingMode _rightMode = HandRenderingMode.IH;
        private Collider _leftHeldCollider;
        private Collider _rightHeldCollider;

        // Reusable probe collider for Physics.ComputePenetration
        private SphereCollider _probe;

        /// <summary>
        /// Returns the Fusion PlayerId of the player this controller belongs to.
        /// Used by HandoverFeedbackController to find the right controller.
        /// </summary>
        public int PlayerId => _networkRig != null && _networkRig.Object != null
            ? _networkRig.Object.InputAuthority.PlayerId
            : -1;

        private void Awake()
        {
            _networkRig = GetComponentInParent<NetworkRig>();

            // Create a hidden probe sphere for penetration checks
            var probeGo = new GameObject("_OH_Probe") { hideFlags = HideFlags.HideAndDontSave };
            probeGo.transform.SetParent(transform);
            _probe = probeGo.AddComponent<SphereCollider>();
            _probe.radius = _grabSettings != null ? _grabSettings.fingertipRadius : 0.012f;
            _probe.enabled = false;
        }

        private void OnEnable()
        {
            if (_playerVisuals != null)
                _playerVisuals.AvatarInitialized.AddListener(OnAvatarInitialized);
        }

        private void OnDisable()
        {
            if (_playerVisuals != null)
                _playerVisuals.AvatarInitialized.RemoveListener(OnAvatarInitialized);
        }

        private void OnAvatarInitialized(AvatarBoneReference boneRef)
        {
            _boneRef = boneRef;
        }

        /// <summary>
        /// Sets the rendering mode for the specified hand side.
        /// Pass heldObjectCollider = null to clear (revert to IH).
        /// </summary>
        public void SetMode(HandRenderingMode mode, Collider heldObjectCollider, bool isLeft)
        {
            if (isLeft) { _leftMode = mode;  _leftHeldCollider  = heldObjectCollider; }
            else        { _rightMode = mode; _rightHeldCollider = heldObjectCollider; }
        }

        private void LateUpdate()
        {
            if (_boneRef == null) return;
            ApplyOHIfNeeded(isLeft: true,  _leftMode,  _leftHeldCollider);
            ApplyOHIfNeeded(isLeft: false, _rightMode, _rightHeldCollider);
        }

        private void ApplyOHIfNeeded(bool isLeft, HandRenderingMode mode, Collider heldCollider)
        {
            if (mode != HandRenderingMode.OH || heldCollider == null) return;

            int side = isLeft ? 0 : 1;
            Transform wrist = isLeft ? _boneRef.LeftHand : _boneRef.RightHand;
            if (wrist == null) return;

            float maxPenetration = 0f;
            Vector3 pushDir = Vector3.zero;

            for (int finger = 0; finger < 5; finger++)
            {
                Transform distal = _boneRef.FingerBones[side, finger, JointIndex.Intermediate];
                if (distal == null) continue;

                if (Physics.ComputePenetration(
                        _probe,    distal.position,    Quaternion.identity,
                        heldCollider, heldCollider.transform.position, heldCollider.transform.rotation,
                        out Vector3 dir, out float dist))
                {
                    if (dist > maxPenetration)
                    {
                        maxPenetration = dist;
                        pushDir = dir;
                    }
                }
            }

            if (maxPenetration > 0f)
                wrist.position += pushDir * maxPenetration;
        }
    }
}
