using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Hardware;
using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using VirtualGrasp;

namespace Application.Scripts.Interaction
{
    /// <summary>
    /// Handles the local grabbing and releasing logic for a hand within the XR rig.
    /// Integrates with the Virtual Grasp system to respond to grasp events and manage interactions with <see cref="Grabbable"/> objects.
    /// </summary>
    public class Grabber : MonoBehaviour
    {
        /// <summary>
        /// The local hand component associated with this grabber.
        /// </summary>
        private HardwareHand _hand;

        /// <summary>
        /// Stores the last collider checked, used internally for potential optimization or logic extensions.
        /// </summary>
        private Collider _lastCheckedCollider;
        
        /// <summary>
        /// Cached reference to the last grabbable component found during collider check.
        /// </summary>
        private Grabbable _lastCheckColliderGrabbable;
        
        /// <summary>
        /// The currently grabbed object, if any.
        /// </summary>
        public Grabbable grabbedObject;
        
        /// <summary>
        /// Reference to the networked counterpart for this grabber,
        /// set during instantiation for the local user.
        /// </summary>
        public NetworkedGrabber networkGrabber;
        
        /// <summary>
        /// Indicates whether the hand is currently performing a grab action.
        /// </summary>
        protected virtual bool IsGrabbing => _hand && _hand.IsGrabbing;
        
        /// <summary>
        /// Initializes the grabber by locating the associated <see cref="HardwareHand"/>.
        /// </summary>
        protected virtual void Awake()
        {
            _hand = GetComponentInParent<HardwareHand>();
            if (_hand == null) Debug.LogError("Grabber should be placed next to an hardware hand");
        }
        
        /// <summary>
        /// Subscribes to grasp-related events from the Virtual Grasp system.
        /// </summary>
        private void OnEnable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> Register Grasp Events");
            VG_Controller.OnObjectGrasped.AddListener(GraspObject);
            VG_Controller.OnObjectReleased.AddListener(ReleaseObject);
        }

        /// <summary>
        /// Unsubscribes from grasp-related events when disabled.
        /// </summary>
        private void OnDisable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> UnregisterGrasp Events");
            VG_Controller.OnObjectGrasped.RemoveListener(GraspObject);
            VG_Controller.OnObjectReleased.RemoveListener(ReleaseObject);
        }

        /// <summary>
        /// Initiates the grab logic for the specified <see cref="Grabbable"/> object.
        /// Updates internal state and sets the hand as grabbing.
        /// </summary>
        /// <param name="grabbable">The object to grab.</param>
        public virtual void Grab(Grabbable grabbable)
        {
            grabbable.Grab(this);
            grabbedObject = grabbable;
            _hand.IsGrabbing = true;
        }
        
        /// <summary>
        /// Releases the currently grabbed object, if any, and updates the internal state.
        /// </summary>
        /// <param name="grabbable">The object to release.</param>
        public virtual void Ungrab(Grabbable grabbable)
        {
            if (grabbedObject == null) return;
            grabbedObject.Ungrab();
            grabbedObject = null;
            _hand.IsGrabbing = false;
        }
        
        /// <summary>
        /// Callback triggered by Virtual Grasp when an object is grasped.
        /// If the grasp matches the correct hand, attempts to grab the object.
        /// </summary>
        /// <param name="graspInfo">Information about the hand and object involved in the grasp.</param>
        private void GraspObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != _hand.Side) return;
            
            Grabbable graspable = graspInfo.m_selectedObject.gameObject.GetComponentInParent<Grabbable>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to grab object {graspable.gameObject.name} with {gameObject.name}");
            
            Grab(graspable);

            // if (graspable.Grab(this))
            // {
            //     //Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> {graspable.gameObject.name} grasped up by {gameObject.name}");
            //     //graspedObject = graspable;
            // }
        }
        
        /// <summary>
        /// Callback triggered by Virtual Grasp when an object is released.
        /// If the release matches the correct hand, attempts to ungrab the object.
        /// </summary>
        /// <param name="graspInfo">Information about the hand and object involved in the release.</param>

        private void ReleaseObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != _hand.Side) return;

            Grabbable releasedObject = graspInfo.m_selectedObject.gameObject.GetComponentInParent<Grabbable>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to release object {releasedObject.gameObject.name} with {gameObject.name}");
            
            Ungrab(grabbedObject);
        }

        // private void Update()
        // {
        //     // Check if the local hand is still grabbing the object
        //     if (grabbedObject != null && IsGrabbing == false)
        //     {
        //         // Object released by this hand
        //         Ungrab(grabbedObject);
        //     }
        // }
    }
}