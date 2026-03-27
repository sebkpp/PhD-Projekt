using System;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Application.Scripts.Utils.Extensions
{
    public static class TransformExtension
    {
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

        /// <summary>
        /// Destroys all children from a transform
        /// </summary>
        public static void DestroyChildren(this Transform t) {
            for (int i = t.childCount - 1; i >= 0; i--)
            {
                Object.Destroy(t.GetChild(i).gameObject);
            }
        }

        /// <summary>
        /// Destroys all children from a transform immediately (use in editor context)
        /// </summary>
        public static void DestroyChildrenImmediate(this Transform t) {
            for (int i = t.childCount - 1; i >= 0; i--)
            {
                Object.DestroyImmediate(t.GetChild(i).gameObject);
            }
        }

        /// <summary>
        /// Finds a specific child inside hierarchy by name
        /// </summary>
        /// <param name="self"></param>
        /// <param name="exactName">Name to search for</param>
        /// <returns>The found transform inside hierarchy, null if nothing was found</returns>
        public static Transform FindRecursive(this Transform self, string exactName) => self.FindRecursive(child => child.name == exactName);

        private static Transform FindRecursive(this Transform self, Func<Transform, bool> selector)
        {
            foreach (Transform child in self)
            {
                if (selector(child))
                {
                    return child;
                }

                var finding = child.FindRecursive(selector);

                if (finding != null)
                {
                    return finding;
                }
            }

            return null;
        }
    }
}