using System;
using UnityEngine;
using UtilsHandOffsets = Application.Scripts.Avatar.Utils.HandOffsets;

namespace Avatar
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

        public void MapTarget(HandOffsets offsetsOffsets)
        {
            MapTarget(offsetsOffsets.wrist, offsetsOffsets.OffsetAxis);

            thumb.MapTarget(offsetsOffsets.thumb, offsetsOffsets.thumb.OffsetAxis);
            index.MapTarget(offsetsOffsets.index, offsetsOffsets.index.OffsetAxis);
            middle.MapTarget(offsetsOffsets.middle, offsetsOffsets.middle.OffsetAxis);
            ring.MapTarget(offsetsOffsets.ring, offsetsOffsets.ring.OffsetAxis);
            little.MapTarget(offsetsOffsets.little, offsetsOffsets.little.OffsetAxis);
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