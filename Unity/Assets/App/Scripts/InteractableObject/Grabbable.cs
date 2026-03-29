using System.Collections.Generic;
using Application.Scripts.Avatar.Grab;
using Application.Scripts.Network.Interactable;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.InteractableObject
{
    /// <summary>
    /// Local component on any graspable object.
    /// Tracks fingertip contacts per GrabHand, manages Rigidbody physics locking,
    /// and keeps a velocity ring buffer for throw-on-release.
    /// All grip logic is driven by GrabHand and NetworkGrabbableObject.
    /// </summary>
    public class Grabbable : MonoBehaviour
    {
        public bool expectedIsKinematic = true;

        [Tooltip("If true and the object has a Rigidbody, apply hand velocity on release.")]
        public bool applyVelocityOnRelease = true;

        [HideInInspector] public Rigidbody rb;
        [HideInInspector] public NetworkGrabbableObject networkGrabbable;

        [Header("Events")]
        public UnityEvent onGrab  = new();
        public UnityEvent onUngrab = new();

        // Fingertip contact count per GrabHand (number of fingertip colliders currently touching)
        private readonly Dictionary<GrabHand, int> _contacts = new();

        #region Contact tracking

        public int GetContactCount(GrabHand hand)
            => _contacts.TryGetValue(hand, out int c) ? c : 0;

        /// <summary>
        /// Called by GrabHand fingertip trigger colliders when entering/exiting this object.
        /// </summary>
        public void RegisterContact(GrabHand hand, bool entering)
        {
            _contacts.TryGetValue(hand, out int count);
            count = entering ? count + 1 : Mathf.Max(0, count - 1);
            if (count == 0) _contacts.Remove(hand);
            else _contacts[hand] = count;
        }

        public void ClearContacts(GrabHand hand) => _contacts.Remove(hand);

        #endregion

        #region Velocity estimation

        private const int VelocityBufferSize = 5;
        private Vector3    _lastPosition;
        private Quaternion _previousRotation;
        private readonly Vector3[]    _lastMoves              = new Vector3[VelocityBufferSize];
        private readonly Vector3[]    _lastAngularVelocities  = new Vector3[VelocityBufferSize];
        private readonly float[]      _lastDeltaTime          = new float[VelocityBufferSize];
        private int _lastMoveIndex;

        public Vector3 Velocity
        {
            get
            {
                Vector3 move = Vector3.zero;
                float   time = 0f;
                for (int i = 0; i < VelocityBufferSize; i++)
                {
                    if (_lastDeltaTime[i] != 0) { move += _lastMoves[i]; time += _lastDeltaTime[i]; }
                }
                return time == 0f ? Vector3.zero : move / time;
            }
        }

        public Vector3 AngularVelocity
        {
            get
            {
                Vector3 sum  = Vector3.zero;
                int     step = 0;
                for (int i = 0; i < VelocityBufferSize; i++)
                {
                    if (_lastDeltaTime[i] != 0) { sum += _lastAngularVelocities[i]; step++; }
                }
                return step == 0 ? Vector3.zero : sum / step;
            }
        }

        private void TrackVelocity()
        {
            _lastMoves[_lastMoveIndex]             = transform.position - _lastPosition;
            _lastAngularVelocities[_lastMoveIndex] = _previousRotation.AngularVelocityChange(transform.rotation, Time.deltaTime);
            _lastDeltaTime[_lastMoveIndex]         = Time.deltaTime;
            _lastMoveIndex                         = (_lastMoveIndex + 1) % VelocityBufferSize;
            _lastPosition                          = transform.position;
            _previousRotation                      = transform.rotation;
        }

        public void ResetVelocityTracking()
        {
            for (int i = 0; i < VelocityBufferSize; i++) _lastDeltaTime[i] = 0f;
            _lastMoveIndex = 0;
        }

        #endregion

        protected virtual void Awake()
        {
            rb = GetComponent<Rigidbody>();
            networkGrabbable = GetComponent<NetworkGrabbableObject>();
            if (rb != null && networkGrabbable == null)
                expectedIsKinematic = rb.isKinematic;
        }

        protected virtual void Update() => TrackVelocity();

        public virtual void LockObjectPhysics()
        {
            if (rb) rb.isKinematic = true;
        }

        public virtual void UnlockObjectPhysics()
        {
            if (rb) rb.isKinematic = expectedIsKinematic;
            if (rb && !rb.isKinematic && applyVelocityOnRelease)
            {
                rb.linearVelocity  = Velocity;
                rb.angularVelocity = AngularVelocity;
            }
            ResetVelocityTracking();
        }
    }
}
