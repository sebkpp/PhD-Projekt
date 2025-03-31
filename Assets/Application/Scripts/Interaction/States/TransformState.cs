using Application.Scripts.Avatar.Utils;
using UnityEngine;

namespace Application.Scripts.Interaction
{
    public struct TransformState : ITransformState
    {
        public Vector3 Position { get; set; }
        public Quaternion Rotation { get; set; }
        
        public TransformState ApplyTransformOffset(TrackingOffsets offset, Quaternion offsetAxis)
        {
            Quaternion rotationOffset = Quaternion.Euler(offset.rotation) * offsetAxis;
            
            return new TransformState
            {
                Position = Position + offset.position,
                Rotation = Rotation * Quaternion.Inverse(rotationOffset)
            };
        }
    }
}