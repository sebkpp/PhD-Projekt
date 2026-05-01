using UnityEngine;

namespace Application.Scripts.Avatar.Utils
{
    /// <summary>
    /// MonoBehaviour that provides a reference to an <see cref="AvatarConfig"/> asset.
    /// This allows other components to access avatar tracking offset configurations at runtime and in inspector.
    /// </summary>
    public class AvatarConfigReference : MonoBehaviour
    {
        [Header("Avatar Configuration")]
        [SerializeField] private AvatarConfig avatarConfig;

        /// <summary>
        /// Gets the assigned <see cref="AvatarConfig"/> used for tracking offset data.
        /// </summary>
        public AvatarConfig Config => avatarConfig;

        /// <summary>
        /// Checks if an <see cref="AvatarConfig"/> is assigned and logs a warning if not.
        /// </summary>
        private void Awake()
        {
            if (avatarConfig == null)
            {
                Debug.LogWarning($"{nameof(AvatarConfigReference)} on {gameObject.name} has no AvatarConfig assigned!", this);
            }
        }
    }
}