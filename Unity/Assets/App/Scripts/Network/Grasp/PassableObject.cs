using System;
using System.Collections;
using System.Collections.Generic;
using Fusion;
using Application.Scripts.Network.Input;
using Network.Grasp;
using UnityEngine;

namespace Application.Scripts.Network.Grasp
{
    [RequireComponent(typeof(NetworkedGraspable))]
    public class PassableObject : NetworkBehaviour
    {
        [Networked] public NetworkRig Giver { get; set; }

        [Networked] public NetworkRig Receiver { get; set; }
        [Networked] private bool IsGraspedByGiver { get; set; }
        [Networked] private bool IsGraspedByReceiver { get; set; }


        private NetworkedGraspable _networkedGraspable;

        private int _graspCounter;

        private void Awake()
        {
            _networkedGraspable = GetComponent<NetworkedGraspable>();
            _networkedGraspable.onDidGrab.AddListener(OnGrasp);
            _networkedGraspable.onDidRelease.AddListener(OnRelease);
        }

        public override void Spawned()
        {
            base.Spawned();

            if (Object.HasStateAuthority)
            {
                Giver = null; // Use PlayerRef.None to represent no holder
                Receiver = null;
            }
        }

        public void OnGrasp(NetworkGrab grabHand)
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

        public void OnRelease(NetworkGrab grabHand)
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
