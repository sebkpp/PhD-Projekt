using System;
using Application.Scripts.Utils.Extensions;
using UnityEngine;

namespace Application.Scripts.Avatar.Utils
{
    /// <summary>
    /// Represents positional and rotational offsets for a single transformable element.
    /// </summary>
    [Serializable]
    public struct TrackingOffsets
    {
        /// <summary>
        /// Positional offset to be applied in local space.
        /// </summary>
        public Vector3 position;
        
        /// <summary>
        /// Rotational offset (Euler angles in degrees) to be applied in local space.
        /// </summary>
        public Vector3 rotation;
    }

    /// <summary>
    /// Contains tracking offsets for the wrist and all five fingers of a hand.
    /// </summary>
    [Serializable]
    public struct HandOffsets
    {
        /// <summary>
        /// Offset configuration for the wrist.
        /// </summary>
        public TrackingOffsets wrist;

        /// <summary>
        /// Offset configuration for the thumb finger joints.
        /// </summary>
        public FingerOffsets thumb;
        
        /// <summary>
        /// Offset configuration for the index finger joints.
        /// </summary>
        public FingerOffsets index;
        
        /// <summary>
        /// Offset configuration for the middle finger joints.
        /// </summary>
        public FingerOffsets middle;
        
        /// <summary>
        /// Offset configuration for the ring finger joints.
        /// </summary>
        public FingerOffsets ring;
        
        /// <summary>
        /// Offset configuration for the pinky finger joints.
        /// </summary>
        public FingerOffsets pinky;
    }

    /// <summary>
    /// Defines orientation and joint-specific tracking offsets for a single finger.
    /// </summary>
    [Serializable]
    public struct FingerOffsets
    {
        [SerializeField] private Axis fingerForward;
        [SerializeField] private Axis fingerUp;
        
        /// <summary>
        /// Computes the rotation offset based on the configured forward and up axes.
        /// This helps orient the finger transform correctly in 3D space.
        /// </summary>
        public Quaternion OffsetAxis => Quaternion.Inverse(Quaternion.LookRotation(fingerForward.ConvertToVector3(), fingerUp.ConvertToVector3()));

        /// <summary>
        /// Tracking offset for the metacarpal joint of the finger.
        /// </summary>
        public TrackingOffsets metacarpal;

        /// <summary>
        /// Tracking offset for the proximal joint of the finger.
        /// </summary>
        public TrackingOffsets proximal;
        
        /// <summary>
        /// Tracking offset for the intermediate joint of the finger.
        /// </summary>
        public TrackingOffsets intermediate;
        
        /// <summary>
        /// Tracking offset for the distal joint of the finger.
        /// </summary>
        public TrackingOffsets distal;
    }
    
    /// <summary>
    /// ScriptableObject that holds avatar-specific tracking offset configurations
    /// for head and hands, including finger joints.
    /// </summary>
    [CreateAssetMenu(fileName = "AvatarConfig", menuName = "SurgerySimulation/AvatarConfig", order = 1)]
    public class AvatarConfig : ScriptableObject
    {
        
        [Header("Head Offset Configs")]
        [SerializeField] private TrackingOffsets head;

        [Header("Hand Offset Configs")]
        [SerializeField] private HandOffsets leftHand;
        [SerializeField] private HandOffsets rightHand;

        [Header("Leg Offset Configs")]
        [SerializeField] private TrackingOffsets leftUpperLeg;
        [SerializeField] private TrackingOffsets leftLowerLeg;
        [SerializeField] private TrackingOffsets rightUpperLeg;
        [SerializeField] private TrackingOffsets rightLowerLeg;

        [Header("Arm Twist Settings")]
        [SerializeField] [Range(0f, 1f)] private float forearmTwistWeight = 0.5f;
        [SerializeField] [Range(0f, 1f)] private float upperArmTwistWeight = 0.2f;

        /// <summary>
        /// Gets the head tracking offset configuration.
        /// </summary>
        public TrackingOffsets Head => head;

        /// <summary>
        /// Gets the left hand tracking offset configuration.
        /// </summary>
        public HandOffsets LeftHand => leftHand;

        /// <summary>
        /// Gets the right hand tracking offset configuration.
        /// </summary>
        public HandOffsets RightHand => rightHand;

        /// <summary>Gets the left upper leg tracking offset configuration.</summary>
        public TrackingOffsets LeftUpperLeg => leftUpperLeg;

        /// <summary>Gets the left lower leg tracking offset configuration.</summary>
        public TrackingOffsets LeftLowerLeg => leftLowerLeg;

        /// <summary>Gets the right upper leg tracking offset configuration.</summary>
        public TrackingOffsets RightUpperLeg => rightUpperLeg;

        /// <summary>Gets the right lower leg tracking offset configuration.</summary>
        public TrackingOffsets RightLowerLeg => rightLowerLeg;

        /// <summary>Gets the forearm twist weight for arm twist interpolation.</summary>
        public float ForearmTwistWeight => forearmTwistWeight;

        /// <summary>Gets the upper arm twist weight for arm twist interpolation.</summary>
        public float UpperArmTwistWeight => upperArmTwistWeight;
    }
}