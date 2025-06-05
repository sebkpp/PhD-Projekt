using Application.Scripts.Interaction;
using Application.Scripts.Network.Interactable;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.InteractableObject
{
    public class Grabbable : MonoBehaviour
    {
        public Vector3 localPositionOffset;
        public Quaternion localRotationOffset;
        public Grabber currentGrabber;
        public bool expectedIsKinematic = true;
        
        [HideInInspector]
        public NetworkedGrabbable networkGrabbable;
        [HideInInspector]
        public Rigidbody rb;
        
        [Tooltip("For object with a rigidbody, if true, apply hand velocity on ungrab")]
        public bool applyVelocityOnRelease = false;

        [Header("Events")]
        [Tooltip("Called only for the local grabber, when they may wait for authority before grabbing. onDidGrab will be called on all users")]
        public UnityEvent<Grabber> onWillGrab = new UnityEvent<Grabber>();
        [Tooltip("Called only for the local grabber, on ungrab")]
        public UnityEvent onUngrab = new UnityEvent();
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
        private int _lastMoveIndex = 0;
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

        void TrackVelocity()
        {
            _lastMoves[_lastMoveIndex] = transform.position - _lastPosition;
            _lastAngularVelocities[_lastMoveIndex] = _previousRotation.AngularVelocityChange(transform.rotation, Time.deltaTime);
            _lastDeltaTime[_lastMoveIndex] = Time.deltaTime;
            _lastMoveIndex = (_lastMoveIndex + 1) % 5;
            _lastPosition = transform.position;
            _previousRotation = transform.rotation;
        }

        void ResetVelocityTracking()
        {
            for (int i = 0; i < VelocityBufferSize; i++) _lastDeltaTime[i] = 0;
            _lastMoveIndex = 0;
        }
        #endregion
        
        
        protected virtual void Awake()
        {
            networkGrabbable = GetComponent<NetworkedGrabbable>();
            rb = GetComponent<Rigidbody>();
            if (networkGrabbable == null && rb != null)
            {
                expectedIsKinematic = rb.isKinematic;
            }
        }

        // protected virtual void Update()
        // {
        //     TrackVelocity();
        //
        //     if (networkGrabbable == null || networkGrabbable.Object == null)
        //     {
        //         // We handle the following if we are not online (online, the Follow will be called by the NetworkGrabbable during FUN and Render)
        //         if (currentGrabber != null)
        //         {
        //             Follow(followedTransform: currentGrabber.transform, localPositionOffset, localRotationOffset);
        //         }
        //     }
        // }
        
        public virtual void Grab(Grabber newGrabber, Transform grabPointTransform = null)
        {
            if (onWillGrab != null) onWillGrab.Invoke(newGrabber);

            // Find grabbable position/rotation in grabber referential
            localPositionOffset = newGrabber.transform.InverseTransformPoint(transform.position);
            localRotationOffset = Quaternion.Inverse(newGrabber.transform.rotation) * transform.rotation;

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
        
        public virtual void LockObjectPhysics()
        {
            // While grabbed, we disable physics forces on the object, to force a position based tracking
            if (rb) rb.isKinematic = true;
        }

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

        public virtual void Follow(Transform followedTransform, Vector3 localPositionOffsetToFollowed, Quaternion localRotationOffsetTofollowed)
        {
            transform.position = followedTransform.TransformPoint(localPositionOffsetToFollowed);
            transform.rotation = followedTransform.rotation * localRotationOffsetTofollowed;
        }
    }
}