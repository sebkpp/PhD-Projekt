using UnityEngine;

namespace Application.Scripts.Interaction
{
    public struct TransformState : ITransformState
    {
        public Vector3 Position { get; set; }
        public Quaternion Rotation { get; set; }
    }
}