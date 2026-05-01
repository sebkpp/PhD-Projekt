using Application.Scripts.Avatar.Grab;
using Application.Scripts.Network.Input;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Interaction
{
    /// <summary>
    /// Per-player networked component on the avatar.
    /// Stores this player's current grip strength and hand position as networked variables
    /// so NetworkGrabbableObject can read them from the state authority.
    /// GrabHand writes EffectiveGrip and HandPosition each frame (local player only).
    /// </summary>
    public class NetworkedGrabber : NetworkBehaviour
    {
        /// <summary>Reference to the NetworkHand on this avatar (set in Spawned).</summary>
        [HideInInspector]
        public NetworkHand hand;

        /// <summary>This player's current effective grip strength (0-1). Written locally, read globally.</summary>
        [Networked] public float EffectiveGrip { get; set; }

        /// <summary>This player's hand world position this tick.</summary>
        [Networked] public Vector3 HandPosition { get; set; }

        public override void Spawned()
        {
            base.Spawned();
            hand = GetComponentInParent<NetworkHand>();
            if (hand == null || !hand.IsLocalNetworkRig) return;

            // Wire ourselves into the local GrabHand so it can write our networked vars
            if (hand.LocalHardwareHand == null) return;
            GrabHand grabHand = hand.LocalHardwareHand.GetComponentInChildren<GrabHand>();
            if (grabHand != null)
                grabHand.networkGrabber = this;
        }
    }
}
