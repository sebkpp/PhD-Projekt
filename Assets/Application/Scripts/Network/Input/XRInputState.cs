using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    /// <summary>
    /// Saves an Input-State. contains Position/Rotation of PlayerArea, Head, Left and Right Hand
    /// </summary>
    public struct XRInputState : INetworkInput
    {
        // Player Area, e.g., for teleportation
        public Vector3 PlayAreaPosition { get; set; }
        public Quaternion PlayAreaRotation { get; set; }

        // Head
        public Vector3 HeadsetPosition { get; set; }
        public Quaternion HeadsetRotation { get; set; }

        // Left Hand
        public HandState LeftHand { get; set; }

        // Right Hand
        public HandState RightHand { get; set; }

    }
}