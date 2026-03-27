using System;
using UnityEngine;
using Application.Scripts.Avatar.Utils;

namespace Application.Scripts.Avatar
{
    [Serializable]
    public class AvatarJointMap
    {
        [SerializeField] private Transform ikTarget;
        [SerializeField] private Transform vrSource;
        
        public Transform IKTarget => ikTarget;

        public Transform VRSource => vrSource;

        public virtual void SetIKTarget(Transform joint)
        {
            ikTarget = joint;
        }

        public virtual void SetVRSource(Transform source)
        {
            vrSource = source;
        }

        public virtual void MapTarget(Vector3 positionOffset, Quaternion rotationOffset)
        {
            if (IKTarget == null || VRSource == null) return;
            
            IKTarget.SetPositionAndRotation(
                VRSource.TransformPoint(positionOffset),
                VRSource.rotation * Quaternion.Inverse(rotationOffset));
        }
        
        public virtual void MapTarget(TrackingOffsets offsets, Quaternion axisRotation)
        {
            MapTarget(offsets.position, Quaternion.Euler(offsets.rotation) * axisRotation);
        }
    }
}
