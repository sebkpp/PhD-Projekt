using System;
using UnityEngine;
using UtilsHandOffsets = Application.Scripts.Avatar.Utils.HandOffsets;

namespace Application.Scripts.Avatar
{
    [Serializable]
    public class AvatarHandJointMap : AvatarJointMap
    {
        public AvatarFingerJointMap thumb;
        public AvatarFingerJointMap index;
        public AvatarFingerJointMap middle;
        public AvatarFingerJointMap ring;
        public AvatarFingerJointMap little;

        public void SetIKTarget(HandSkeleton handSkeleton)
        {
            SetIKTarget(handSkeleton.hand);
            
            thumb.SetIKTarget(handSkeleton.thumb);
            index.SetIKTarget(handSkeleton.index);
            middle.SetIKTarget(handSkeleton.middle);
            ring.SetIKTarget(handSkeleton.ring);
            little.SetIKTarget(handSkeleton.little);
        }

        public void MapTarget(UtilsHandOffsets handOffsets)
        {
            MapTarget(handOffsets.wrist, Quaternion.identity);
            thumb.MapTarget(handOffsets.thumb, handOffsets.thumb.OffsetAxis);
            index.MapTarget(handOffsets.index, handOffsets.index.OffsetAxis);
            middle.MapTarget(handOffsets.middle, handOffsets.middle.OffsetAxis);
            ring.MapTarget(handOffsets.ring, handOffsets.ring.OffsetAxis);
            little.MapTarget(handOffsets.pinky, handOffsets.pinky.OffsetAxis);
        }
    }
}