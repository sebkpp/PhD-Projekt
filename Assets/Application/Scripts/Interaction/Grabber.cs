using System.Collections.Generic;
using Application.Scripts.Avatar;
using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using UnityEngine;

namespace Application.Scripts.Interaction
{
    public class Grabber : MonoBehaviour
    {
        HardwareHand hand;

        Collider lastCheckedCollider;
        Grabbable lastCheckColliderGrabbable;
        public Grabbable grabbedObject;
        // Will be set by the NetworkGrabber for the local user itself, when it spawns
        public NetworkedGrabber networkGrabber;
        protected virtual void Awake()
        {
            //hand = GetComponentInParent<HardwareHand>();
            //if (hand == null) Debug.LogError("Grabber should be placed next to an hardware hand");
        }

        protected virtual bool IsGrabbing => hand && hand.isGrabbing;

        private void OnTriggerStay(Collider other)
        {
            if (enabled == false) return;
            // Exit if an object is already grabbed
            if (grabbedObject != null)
            {
                // It is already the grabbed object or another, but we don't allow shared grabbing here
                return;
            }

            Grabbable grabbable;

            if (lastCheckedCollider == other)
            {
                grabbable = lastCheckColliderGrabbable;
            }
            else
            {
                grabbable = other.GetComponentInParent<Grabbable>();
            }
            // To limit the number of GetComponent calls, we cache the latest checked collider grabbable result
            lastCheckedCollider = other;
            lastCheckColliderGrabbable = grabbable;
            if (grabbable != null)
            {
                if (IsGrabbing)
                {
                    Grab(grabbable);
                } 
            }
        }
        
        public virtual void Grab(Grabbable grabbable)
        {
            grabbable.Grab(this);
            grabbedObject = grabbable;
        }

        public virtual void Ungrab(Grabbable grabbable)
        {
            if (grabbedObject == null) return;
            grabbedObject.Ungrab();
            grabbedObject = null;
        }

        private void Update()
        {
            // Check if the local hand is still grabbing the object
            if (grabbedObject != null && IsGrabbing == false)
            {
                // Object released by this hand
                Ungrab(grabbedObject);
            }
        }
    }
}