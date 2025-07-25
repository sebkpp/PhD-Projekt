using Application.Scripts.Interaction;
using Application.Scripts.Network.Interactable;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.InteractableObject
{
    /// <summary>
    /// Represents an object that can be grabbed and manipulated by a <see cref="Grabber"/>.
    /// Handles physics toggling, velocity tracking and local follow behavior.
    /// </summary>
    public class Grabbable : MonoBehaviour
    {
        /// <summary>
        /// Local position offset relative to the hand when grabbed.
        /// </summary>
        public Vector3 localPositionOffset;
        
        /// <summary>
        /// Local rotation offset relative to the hand when grabbed.
        /// </summary>
        public Quaternion localRotationOffset;
        
        /// <summary>
        /// Reference to the current <see cref="Grabber"/> holding this object.
        /// </summary>
        public Grabber currentGrabber;
        
        /// <summary>
        /// Whether the rigidbody should be kinematic after being released (default value caching).
        /// </summary>
        public bool expectedIsKinematic = true;
        
        /// <summary>
        /// Network synchronization component for multiplayer grab interactions.
        /// </summary>
        public NetworkedGrabbable networkGrabbable;
        
        /// <summary>
        /// Cached Rigidbody reference (optional).
        /// </summary>
        [HideInInspector]
        public Rigidbody rb;
        
        /// <summary>
        /// If true and the object has a Rigidbody, hand velocity will be applied on release.
        /// </summary>
        [Tooltip("For object with a rigidbody, if true, apply hand velocity on ungrab")]
        public bool applyVelocityOnRelease;

        /// <summary>
        /// Invoked on the local client before grabbing is confirmed (e.g. waiting for network authority).
        /// </summary>
        [Header("Events")]
        [Tooltip("Called only for the local grabber, when they may wait for authority before grabbing. onDidGrab will be called on all users")]
        public UnityEvent<Grabber> onWillGrab = new UnityEvent<Grabber>();
        
        /// <summary>
        /// Invoked on the local client when the object is released.
        /// </summary>
        [Tooltip("Called only for the local grabber, on ungrab")]
        public UnityEvent onUngrab = new UnityEvent();
        
        /// <summary>
        /// Invoked on the local client when the object is successfully grabbed.
        /// </summary>
        [Tooltip("Called only for the local grabber, on grab")]
        public UnityEvent onGrab = new UnityEvent();
        
        #region Velocity estimation
        // Velocity computation
        private const int VelocityBufferSize = 5;
        private Vector3 _lastPosition;
        private Quaternion _previousRotation;
        private Vector3[] _lastMoves = new Vector3[VelocityBufferSize];
        private Vector3[] _lastAngularVelocities = new Vector3[VelocityBufferSize];
        private float[] _lastDeltaTime = new float[VelocityBufferSize];
        private int _lastMoveIndex;
        
        /// <summary>
        /// Computes the average linear velocity of the object over the last few frames.
        /// </summary>
        Vector3 Velocity
        {
            get
            {
                Vector3 move = Vector3.zero;
                float time = 0;
                for (int i = 0; i < VelocityBufferSize; i++)
                {
                    if (_lastDeltaTime[i] != 0)
                    {
                        move += _lastMoves[i];
                        time += _lastDeltaTime[i];
                    }
                }
                if (time == 0) return Vector3.zero;
                return move / time;
            }
        }

        /// <summary>
        /// Computes the average angular velocity of the object over the last few frames.
        /// </summary>
        Vector3 AngularVelocity
        {
            get
            {
                Vector3 culmulatedAngularVelocity = Vector3.zero;
                int step = 0;
                for (int i = 0; i < VelocityBufferSize; i++)
                {
                    if (_lastDeltaTime[i] != 0)
                    {
                        culmulatedAngularVelocity += _lastAngularVelocities[i];
                        step++;
                    }
                }
                if (step == 0) return Vector3.zero;
                return culmulatedAngularVelocity / step;
            }
        }

        /// <summary>
        /// Records velocity and angular velocity for use when releasing.
        /// </summary>
        void TrackVelocity()
        {
            _lastMoves[_lastMoveIndex] = transform.position - _lastPosition;
            _lastAngularVelocities[_lastMoveIndex] = _previousRotation.AngularVelocityChange(transform.rotation, Time.deltaTime);
            _lastDeltaTime[_lastMoveIndex] = Time.deltaTime;
            _lastMoveIndex = (_lastMoveIndex + 1) % 5;
            _lastPosition = transform.position;
            _previousRotation = transform.rotation;
        }

        /// <summary>
        /// Clears stored velocity data.
        /// </summary>
        void ResetVelocityTracking()
        {
            for (int i = 0; i < VelocityBufferSize; i++) _lastDeltaTime[i] = 0;
            _lastMoveIndex = 0;
        }
        #endregion
        
        /// <summary>
        /// Initializes components and stores rigidbody kinematic state.
        /// </summary>
        protected virtual void Awake()
        {
            networkGrabbable = GetComponent<NetworkedGrabbable>();
            rb = GetComponent<Rigidbody>();
            if (networkGrabbable == null && rb != null)
            {
                expectedIsKinematic = rb.isKinematic;
            }
        }

        /// <summary>
        /// Updates velocity tracking and, if not networked, makes the object follow the grabber.
        /// </summary>
        protected virtual void Update()
        {
            TrackVelocity();
        
            if (networkGrabbable == null || networkGrabbable.Object == null)
            {
                // We handle the following if we are not online (online, the Follow will be called by the NetworkGrabbable during FUN and Render)
                if (currentGrabber != null)
                {
                    Follow(followedTransform: currentGrabber.transform, localPositionOffset, localRotationOffset);
                }
            }
        }

        /// <summary>
        /// Draws debug gizmos in the editor to visualize grab point.
        /// </summary>
        public void OnDrawGizmos()
        {
            if (currentGrabber)
            {
                Gizmos.color = Color.blue;
                Vector3 worldPos = currentGrabber.networkGrabber.hand.AvatarHand.TransformPoint(localPositionOffset);
                Debug.Log($"Local: {currentGrabber.networkGrabber.hand.AvatarHand.position.ToString("F5")}");
                Gizmos.DrawSphere(worldPos, 0.05f);
            }
        }

        /// <summary>
        /// Handles the logic of being grabbed by a <see cref="Grabber"/>.
        /// Sets local offsets, locks physics, triggers events, and optionally syncs over network.
        /// </summary>
        /// <param name="newGrabber">The grabber that is grabbing the object.</param>
        /// <param name="grabPointTransform">Optional transform representing the grab point.</param>
        public virtual void Grab(Grabber newGrabber, Transform grabPointTransform = null)
        {
            if (onWillGrab != null) onWillGrab.Invoke(newGrabber);

            // Find grabbable position/rotation in grabber referential
            localPositionOffset = newGrabber.networkGrabber.hand.AvatarHand.InverseTransformPoint(transform.position);
            localRotationOffset = Quaternion.Inverse(newGrabber.networkGrabber.hand.AvatarHand.rotation) * transform.rotation;

            currentGrabber = newGrabber;
            Debug.Log("Grabbed");

            if (networkGrabbable)
            {
                networkGrabbable.LocalGrab();
            }
            else
            {
                // We handle the following if we are not online (online, the DidGrab will be called by the NetworkGrabbable DidGrab, itself called on all clients by HandleGrabberChange when the grabber networked var has changed)
                LockObjectPhysics();
            }
            if (onGrab != null) onGrab.Invoke();
        }

        /// <summary>
        /// Releases the object from being held. Re-enables physics and triggers events or network sync.
        /// </summary>
        public virtual void Ungrab()
        {
            currentGrabber = null;
            if (networkGrabbable)
            {
                networkGrabbable.LocalUngrab();
            }
            else
            {
                // We handle the following if we are not online (online, the DidGrab will be called by the NetworkGrabbable DidUngrab, itself called on all clients by HandleGrabberChange when the grabber networked var has changed)
                UnlockObjectPhysics();
            }
            if (onUngrab != null) onUngrab.Invoke();
        }
        
        /// <summary>
        /// Disables rigidbody physics by setting <see cref="Rigidbody.isKinematic"/> to true.
        /// Called when object is grabbed.
        /// </summary>
        public virtual void LockObjectPhysics()
        {
            // While grabbed, we disable physics forces on the object, to force a position based tracking
            if (rb) rb.isKinematic = true;
        }

        /// <summary>
        /// Re-enables physics and applies tracked velocity if configured.
        /// Called when object is released.
        /// </summary>
        public virtual void UnlockObjectPhysics()
        {
            // We restore the default isKinematic state if needed
            if (rb) rb.isKinematic = expectedIsKinematic;

            // We apply release velocity if needed
            if (rb && rb.isKinematic == false && applyVelocityOnRelease)
            {
                rb.linearVelocity = Velocity;
                rb.angularVelocity = AngularVelocity;
            }

            ResetVelocityTracking();
        }

        /// <summary>
        /// Updates the object's world position and rotation to follow a given transform with an offset.
        /// </summary>
        /// <param name="followedTransform">The transform to follow (typically a hand).</param>
        /// <param name="localPositionOffsetToFollowed">Local position offset relative to the followed transform.</param>
        /// <param name="localRotationOffsetTofollowed">Local rotation offset relative to the followed transform.</param>
        public virtual void Follow(Transform followedTransform, Vector3 localPositionOffsetToFollowed, Quaternion localRotationOffsetTofollowed)
        {
            transform.position = followedTransform.TransformPoint(localPositionOffsetToFollowed);
            transform.rotation = followedTransform.rotation * localRotationOffsetTofollowed;
        }
    }
}