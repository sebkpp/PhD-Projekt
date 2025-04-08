using Application.Scripts.Avatar.Utils;
using UnityEngine;

namespace Application.Scripts.Interaction.States
{
    public struct FingerState
    {
        public TransformState Proximal { get; set; }
        public TransformState Intermediate { get; set; }
        public TransformState Distal { get; set; }
        
        public FingerState ApplyFingerPoseOffset(FingerOffsets offset)
        {
            Quaternion axis = offset.OffsetAxis;
            
            return new FingerState
            {
                Proximal = Proximal.ApplyTransformOffset(offset.proximal, axis),
                Intermediate = Intermediate.ApplyTransformOffset(offset.intermediate, axis),
                Distal = Distal.ApplyTransformOffset(offset.distal, axis)
            };
        }
    }
    
    public struct HandState
    {
        public TransformState Wrist { get; set; }
        
        public FingerState Thumb { get; set; }
        public FingerState Index { get; set; }
        public FingerState Middle { get; set; }
        public FingerState Ring { get; set; }
        public FingerState Pinky { get; set; }
        
        
        public HandState ApplyHandPoseOffset(HandOffsets handOffsets)
        {
            return new HandState
            {
                Wrist = Wrist.ApplyTransformOffset(handOffsets.wrist, Quaternion.identity),
                
                Thumb = Thumb.ApplyFingerPoseOffset(handOffsets.thumb),
                Index = Index.ApplyFingerPoseOffset(handOffsets.index),
                Middle = Middle.ApplyFingerPoseOffset(handOffsets.middle),
                Ring = Ring.ApplyFingerPoseOffset(handOffsets.ring),
                Pinky = Pinky.ApplyFingerPoseOffset(handOffsets.pinky)
            };
        }
    }
}