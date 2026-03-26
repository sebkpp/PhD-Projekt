using UnityEngine;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Represents a physical hand device in the XR rig.
    /// Tracks the hand's transform and grabbing state.
    /// </summary>
    public class HardwareHand : MonoBehaviour
    {
        /// <summary>
        /// Specifies which hand this component represents (e.g., left or right).
        /// </summary>
        public RigPart side;
        
        /// <summary>
        /// Indicates whether the hand is currently performing a grab action.
        /// </summary>
        public bool isGrabbing = false;
        
        /// <summary>
        /// Stores detailed tracking data for the hand, including finger poses.
        /// </summary>
        public HandTrackingData HandTrackingData;
    }
}