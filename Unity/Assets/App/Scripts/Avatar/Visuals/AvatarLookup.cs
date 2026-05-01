using UnityEngine;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Provides access to key reference points on the avatar's body.
    /// Used for positioning, alignment, and spatial queries relative to the avatar.
    /// </summary>
    public class AvatarLookup : MonoBehaviour
    {
        [SerializeField] private Transform avatarRoot;
        [SerializeField] private Transform avatarHead;
        [SerializeField] private Transform avatarMiddleEye;
        [SerializeField] private Transform avatarFeet;

        /// <summary>
        /// Gets the transform representing the avatar's feet position.
        /// Typically used for ground alignment or height calculation.
        /// </summary>
        public Transform AvatarFeet => avatarFeet;

        /// <summary>
        /// Gets the transform representing the avatar's head position.
        /// Useful for aligning cameras or head-related effects.
        /// </summary>
        public Transform AvatarHead => avatarHead;

        /// <summary>
        /// Gets the root transform of the avatar.
        /// Often used as the base for avatar positioning and animation.
        /// </summary>
        public Transform AvatarRoot => avatarRoot;

        /// <summary>
        /// Gets the transform positioned between the avatar's eyes.
        /// Useful for aligning stereo cameras or calculating gaze direction.
        /// </summary>
        public Transform AvatarMiddleEye => avatarMiddleEye;
    }
}
