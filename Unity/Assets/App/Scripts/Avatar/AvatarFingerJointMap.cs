using System;
using UnityEngine;
using UtilsFingerOffsets = Application.Scripts.Avatar.Utils.FingerOffsets;

namespace Application.Scripts.Avatar
{
    [Serializable]
    public class AvatarFingerJointMap
    {
        public AvatarJointMap proximal;
        public AvatarJointMap intermediate;
        public AvatarJointMap distal;

        public void SetIKTarget(FingerSkeleton fingerSkeleton)
        {
            proximal.SetIKTarget(fingerSkeleton.proximal.transform);
            intermediate.SetIKTarget(fingerSkeleton.intermediate.transform);
            distal.SetIKTarget(fingerSkeleton.distal.transform);
        }
        
        public void MapTarget(UtilsFingerOffsets fingerOffsets, Quaternion offsetAxis)
        {
            proximal.MapTarget(fingerOffsets.proximal, offsetAxis);
            intermediate.MapTarget(fingerOffsets.intermediate, offsetAxis);
            distal.MapTarget(fingerOffsets.distal, offsetAxis);
        }
    }
}