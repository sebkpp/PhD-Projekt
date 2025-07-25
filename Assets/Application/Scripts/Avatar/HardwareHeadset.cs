using Fusion;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Represents the local user's physical headset in the XR rig.
    /// Handles access to its <see cref="NetworkTransform"/> component,
    /// which is used to synchronize the headset's position and rotation over the network.
    /// </summary>
    public class HardwareHeadset: MonoBehaviour
    {
        /// <summary>
        /// The <see cref="NetworkTransform"/> component responsible for synchronizing
        /// the headset's position and rotation across the network.
        /// </summary>
        public NetworkTransform networkTransform;
        
        /// <summary>
        /// Unity lifecycle method called on object instantiation.
        /// Ensures that the <see cref="networkTransform"/> reference is set.
        /// </summary>
        private void Awake()
        {
            if (networkTransform == null) networkTransform = GetComponent<NetworkTransform>();
        }
    }
}