using System;
using Application.Scripts.Utils.Extensions;
using UnityEngine;

namespace Application.Scripts.Avatar.Utils
{
    [Serializable]
    public struct TrackingOffsets
    {
        public Vector3 position;
        public Vector3 rotation;
    }

    [Serializable]
    public struct HandOffsets
    {
        public TrackingOffsets wrist;

        public FingerOffsets thumb;
        public FingerOffsets index;
        public FingerOffsets middle;
        public FingerOffsets ring;
        public FingerOffsets pinky;
    }

    [Serializable]
    public struct FingerOffsets
    {
        [SerializeField] private Axis fingerForward;
        [SerializeField] private Axis fingerUp;
        
        public Quaternion OffsetAxis => Quaternion.Inverse(Quaternion.LookRotation(fingerForward.ConvertToVector3(), fingerUp.ConvertToVector3()));

        public TrackingOffsets proximal;
        public TrackingOffsets intermediate;
        public TrackingOffsets distal;
    }
    
    [CreateAssetMenu(fileName = "AvatarConfig", menuName = "SurgerySimulation/AvatarConfig", order = 1)]
    public class AvatarConfig : ScriptableObject
    {
        [Header("Head Offset Configs")]
        [SerializeField] private TrackingOffsets head;

        [Header("Hand Offset Configs")]
        [SerializeField] private HandOffsets leftHand;
        [SerializeField] private HandOffsets rightHand;
        
        public TrackingOffsets Head => head;
        public HandOffsets LeftHand => leftHand;
        public HandOffsets RightHand => rightHand;
    }
}