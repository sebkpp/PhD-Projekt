using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    /// <summary>
    /// Represents the networked headset component of a player rig in a Fusion-based multiplayer environment.
    /// This class is responsible for synchronizing the transform of the VR headset across the network.
    /// </summary>
    /// <remarks>
    /// This component should be attached to the GameObject representing the headset in the player's avatar.
    /// It requires a <see cref="NetworkTransform"/> to synchronize its position and rotation.
    /// </remarks>
    public class NetworkHeadset : NetworkBehaviour
    {
        /// <summary>
        /// Defines the recommended execution order of this component.
        /// Slightly later than <see cref="NetworkRig"/> to ensure dependencies are resolved in time.
        /// </summary>
        // ReSharper disable once InconsistentNaming
        public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;
        
        /// <summary>
        /// The <see cref="NetworkTransform"/> used to synchronize the headset's position and rotation over the network.
        /// This reference is initialized automatically during <see cref="Awake"/> if not already assigned.
        /// </summary>
        [HideInInspector]
        public NetworkTransform networkTransform;

        /// <summary>
        /// Unity Awake method.
        /// Ensures the <see cref="networkTransform"/> reference is set to the attached <see cref="NetworkTransform"/> component.
        /// </summary>
        private void Awake()
        {
            if (networkTransform == null) networkTransform = GetComponent<NetworkTransform>();
        }
    }
}