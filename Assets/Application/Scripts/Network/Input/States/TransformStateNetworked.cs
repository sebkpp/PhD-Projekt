using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input.States
{
    /// <summary>
    /// Represents a networked transform state, including position and rotation,
    /// used for synchronizing object transforms across the network in a Fusion-based multiplayer context.
    /// </summary>
    /// <remarks>
    /// This struct is intended to be lightweight and serializable by Fusion,
    /// and is commonly used to transmit positional and rotational data for VR devices,
    /// avatars, or interactable objects.
    /// </remarks>
    public struct TransformStateNetworked :  INetworkStruct
    {
        /// <summary>
        /// The world-space position of the object.
        /// </summary>
        public Vector3 Position;
        
        /// <summary>
        /// The world-space rotation of the object.
        /// </summary>
        public Quaternion Rotation;
    }
}