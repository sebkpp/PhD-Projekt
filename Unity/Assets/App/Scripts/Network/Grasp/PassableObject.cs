using System;
using System.Collections;
using System.Collections.Generic;
using Fusion;
using Application.Scripts.Network.Input;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Network.Interactable;
using UnityEngine;

namespace Application.Scripts.Network.Grasp
{
    [RequireComponent(typeof(NetworkedGrabbable))]
    public class PassableObject : NetworkBehaviour
    {
        [Networked] public NetworkRig Giver { get; set; }

        [Networked] public NetworkRig Receiver { get; set; }
        [Networked] private bool IsGraspedByGiver { get; set; }
        [Networked] private bool IsGraspedByReceiver { get; set; }


        private NetworkedGrabbable _networkedGrabbable;

        private int _graspCounter;

        private void Awake()
        {
            _networkedGrabbable = GetComponent<NetworkedGrabbable>();
            _networkedGrabbable.onDidGrab.AddListener(OnGrasp);
            _networkedGrabbable.onDidUngrab.AddListener(OnRelease);
        }

        public override void Spawned()
        {
            base.Spawned();

            if (Object.HasStateAuthority)
            {
                Giver = null;
                Receiver = null;
            }
        }

        public void OnGrasp(NetworkedGrabber grabHand)
        {
            if (Object.HasStateAuthority)
            {
                switch (_graspCounter)
                {
                    case 0:
                        Giver = grabHand.GetComponentInParent<NetworkRig>();
                        _graspCounter++;
                        break;
                    case 1:
                        Receiver = grabHand.GetComponentInParent<NetworkRig>();
                        _graspCounter++;
                        break;
                    case 2:
                        return;
                }
            }
        }

        public void OnRelease()
        {
            if (Object.HasStateAuthority)
            {
                switch (_graspCounter)
                {
                    case 2:
                        Giver = null;
                        _graspCounter--;
                        break;
                    case 1:
                        Receiver = null;
                        _graspCounter--;
                        break;
                    case 0:
                        return;
                }
            }
        }

        public void TransferInputAuthority(PlayerRef passTo)
        {
            if (Object.HasStateAuthority)
            {
                Object.AssignInputAuthority(passTo);
            }
        }
    }
}
