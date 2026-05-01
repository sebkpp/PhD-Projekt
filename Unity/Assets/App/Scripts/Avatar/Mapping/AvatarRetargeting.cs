using UnityEngine;

namespace Application.Scripts.Avatar.Mapping
{
    /// <summary>
    /// One-time height calibration: shifts the avatar root so the avatar's eye height
    /// matches the player's real HMD height.  Avatar feet stay on the ground plane.
    /// </summary>
    public static class AvatarRetargeting
    {
        /// <summary>
        /// Adjusts <paramref name="avatarRoot"/> vertical position so the avatar's eyes
        /// align with the HMD.
        /// </summary>
        /// <param name="avatarRoot">Root transform of the instantiated avatar.</param>
        /// <param name="avatarHeadBone">The avatar's head bone (Bip01 Head).</param>
        /// <param name="hmdWorldPosition">Current world position of the HMD Camera.</param>
        /// <returns>The vertical offset applied (positive = avatar was moved down).</returns>
        public static float Calibrate(Transform avatarRoot, Transform avatarHeadBone, Vector3 hmdWorldPosition)
        {
            float avatarEyeHeight = avatarHeadBone.position.y;
            float hmdHeight       = hmdWorldPosition.y;
            float offset          = avatarEyeHeight - hmdHeight;

            Vector3 pos = avatarRoot.position;
            pos.y -= offset;
            avatarRoot.position = pos;

            return offset;
        }
    }
}
