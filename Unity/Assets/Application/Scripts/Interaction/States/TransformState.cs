using UnityEngine;

namespace Application.Scripts.Interaction.States
{
    /// <summary>
    /// Represents a simplified transform state containing position and rotation.
    /// Useful for serializing or transferring transform data without directly referencing Unity's Transform component.
    /// </summary>
    public struct TransformState
    {
        /// <summary>
        /// The position of the transform in world or local space.
        /// </summary>
        public Vector3 Position;

        /// <summary>
        /// The rotation of the transform in world or local space.
        /// </summary>
        public Quaternion Rotation;
        
        /// <summary>
        /// Returns a string representation of the transform state including position and Euler angles.
        /// </summary>
        /// <returns>A formatted string with position and rotation values.</returns>
        public override string ToString()
        {
            return $"Position: {Position}, Rotation: {Rotation.eulerAngles}";
        }
    }
}