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
    }
}