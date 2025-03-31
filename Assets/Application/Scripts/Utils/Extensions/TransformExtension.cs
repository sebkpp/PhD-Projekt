using System;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using UnityEngine;

namespace Application.Scripts.Utils.Extensions
{
    public static class TransformExtension
    {
        public static Vector3 ApplyOffset(this Transform t, Vector3 positionOffset)
        {
            return t.TransformPoint(positionOffset);
        }

        public static Quaternion ApplyOffsetRotation(this Transform t, Vector3 rotationOffset)
        {
            return t.rotation * Quaternion.Euler(rotationOffset);
        }
        
        public static Quaternion ApplyOffsetLocalRotation(this Transform t, Vector3 rotationOffset)
        {
            return t.localRotation * Quaternion.Euler(rotationOffset);
        }

        public static TransformState GetTransformState(this Transform t)
        {
            TransformState state = new TransformState()
            {
                Position = t.position,
                Rotation = t.rotation
            };

            return state;
        }

        public static void SetTransformState(this Transform t, TransformState state)
        {
            t.position = state.Position;
            t.rotation = state.Rotation;
        }
        
        /// <summary>
        /// Converts Axis to Vector3
        /// </summary>
        /// <param name="axis"></param>
        /// <returns></returns>
        /// <exception cref="ArgumentOutOfRangeException"></exception>
        public static Vector3 ConvertToVector3(this Axis axis) {
            return axis switch
            {
                Axis.X => Vector3.right,
                Axis.XNeg => Vector3.left,
                Axis.Y => Vector3.up,
                Axis.YNeg => Vector3.down,
                Axis.Z => Vector3.forward,
                Axis.ZNeg => Vector3.back,
                _ => throw new ArgumentOutOfRangeException(nameof(axis), axis, "No valid Axis")
            };
        }
    }
}