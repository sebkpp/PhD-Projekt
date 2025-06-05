using Application.Scripts.Avatar;
using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using VirtualGrasp;

namespace Application.Scripts.Interaction
{
    public class Grabber : MonoBehaviour
    {
        private HardwareHand _hand;

        private Collider _lastCheckedCollider;
        private Grabbable _lastCheckColliderGrabbable;
        public Grabbable grabbedObject;
        
        // Will be set by the NetworkGrabber for the local user itself, when it spawns
        public NetworkedGrabber networkGrabber;
        
        protected virtual bool IsGrabbing => _hand && _hand.isGrabbing;

        
        
        protected virtual void Awake()
        {
            _hand = GetComponentInParent<HardwareHand>();
            if (_hand == null) Debug.LogError("Grabber should be placed next to an hardware hand");
        }
        
        private void OnEnable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> Register Grasp Events");
            VG_Controller.OnObjectGrasped.AddListener(GraspObject);
            VG_Controller.OnObjectReleased.AddListener(ReleaseObject);
        }

        private void OnDisable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> UnregisterGrasp Events");
            VG_Controller.OnObjectGrasped.RemoveListener(GraspObject);
            VG_Controller.OnObjectReleased.RemoveListener(ReleaseObject);
        }

        public virtual void Grab(Grabbable grabbable)
        {
            grabbable.Grab(this);
            grabbedObject = grabbable;
            _hand.isGrabbing = true;
        }
        
        public virtual void Ungrab(Grabbable grabbable)
        {
            if (grabbedObject == null) return;
            grabbedObject.Ungrab();
            grabbedObject = null;
            _hand.isGrabbing = false;
        }
        
        private void GraspObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != _hand.side) return;
            
            Grabbable graspable = graspInfo.m_selectedObject.gameObject.GetComponentInParent<Grabbable>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to grab object {graspable.gameObject.name} with {gameObject.name}");
            
            Grab(graspable);

            // if (graspable.Grab(this))
            // {
            //     //Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> {graspable.gameObject.name} grasped up by {gameObject.name}");
            //     //graspedObject = graspable;
            // }
        }
        
        private void ReleaseObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != _hand.side) return;

            Grabbable releasedObject = graspInfo.m_selectedObject.gameObject.GetComponentInParent<Grabbable>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to release object {releasedObject.gameObject.name} with {gameObject.name}");
            if (releasedObject.networkGrabbable)
            {
                // Transform networkedObjectTransform = releasedObject.networkGrabbable.transform;
                //
                // _unGrabPosition = networkedObjectTransform.position;
                // _unGrabRotation = networkedObjectTransform.rotation;
                // _unGrabVelocity = releasedObject.Velocity;
                // _unGrabAngularVelocity = releasedObject.AngularVelocity;
            }

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