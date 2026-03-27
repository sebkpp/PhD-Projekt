using System;
using UnityEngine;
using UnityEngine.Animations.Rigging;

namespace Application.Scripts.CustomExtensions
{
    public static class AxisExtensions
    {
        /// <summary>
        /// Converts Axis to Vector3
        /// </summary>
        /// <param name="axis"></param>
        /// <returns></returns>
        /// <exception cref="ArgumentOutOfRangeException"></exception>
        public static Vector3 ConvertToVector3(this MultiAimConstraintData.Axis axis) {
            return axis switch
            {
                MultiAimConstraintData.Axis.X => Vector3.right,
                MultiAimConstraintData.Axis.X_NEG => Vector3.left,
                MultiAimConstraintData.Axis.Y => Vector3.up,
                MultiAimConstraintData.Axis.Y_NEG => Vector3.down,
                MultiAimConstraintData.Axis.Z => Vector3.forward,
                MultiAimConstraintData.Axis.Z_NEG => Vector3.back,
                _ => throw new ArgumentOutOfRangeException(nameof(axis), axis, "No valid Axis")
            };
        }
    }
}