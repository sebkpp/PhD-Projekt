using Application.Scripts.Interaction;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    /// <summary>
    /// Saves an Input-State. contains Position/Rotation of PlayerArea, Head, Left and Right Hand
    /// </summary>
    public struct XRInputState :  IXRInputState<TransformState, HandState>
    {
        // Player Area, e.g., for teleportation
        public TransformState PlayArea { get; set; }
        
        // Head
        public TransformState Head { get; set; }

        // Left Hand
        public HandState LeftHand { get; set; }

        // Right Hand
        public HandState RightHand { get; set; }

    }
}