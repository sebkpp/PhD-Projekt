using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Interaction
{
    public class NetworkedGrabber : NetworkBehaviour
    {
        [HideInInspector]
        public NetworkHand hand;
        
        public override void Spawned()
        {
            base.Spawned();
            hand = GetComponentInParent<NetworkHand>();
            if (hand && hand.IsLocalNetworkRig)
            {
                // References itself in its local counterpart, to simplify the lookup during local grabbing
                if (hand.LocalHardwareHand)
                {
                    Grabber grabber = hand.LocalHardwareHand.GetComponentInChildren<Grabber>();
                    grabber.networkGrabber = this;
                }
            }
        }
    }
}