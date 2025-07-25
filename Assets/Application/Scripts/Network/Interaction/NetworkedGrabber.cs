using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Interaction
{
    /// <summary>
    /// Represents the networked counterpart of a local <see cref="Grabber"/> component,
    /// allowing the synchronization of grab interactions in a multiplayer environment.
    /// </summary>
    /// <remarks>
    /// This class is part of the multiplayer interaction system. When the object is spawned
    /// on the network, it attempts to find the corresponding local hardware hand and
    /// assigns itself to its local <see cref="Grabber"/> component.
    /// 
    /// This enables local input (e.g. grabbing via hardware hand tracking) to be correctly
    /// linked to its network representation, so other players can see and react to the action.
    /// </remarks>
    public class NetworkedGrabber : NetworkBehaviour
    {
        /// <summary>
        /// Reference to the <see cref="NetworkHand"/> associated with this grabber.
        /// This is automatically set during <see cref="Spawned"/>.
        /// </summary>
        [HideInInspector]
        public NetworkHand hand;
        
        /// <summary>
        /// Called by Fusion when the networked object is spawned.
        /// Initializes the reference to the local <see cref="Grabber"/> component
        /// if this instance belongs to the local player.
        /// </summary>
        public override void Spawned()
        {
            base.Spawned();
            hand = GetComponentInParent<NetworkHand>();
            if (!hand || !hand.IsLocalNetworkRig) return;
            
            // References itself in its local counterpart, to simplify the lookup during local grabbing
            if (!hand.LocalHardwareHand) return;
            
            Grabber grabber = hand.LocalHardwareHand.GetComponentInChildren<Grabber>();
            grabber.networkGrabber = this;
        }
    }
}