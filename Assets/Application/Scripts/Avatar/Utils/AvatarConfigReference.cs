using UnityEngine;

namespace Application.Scripts.Avatar.Utils
{
    public class AvatarConfigReference : MonoBehaviour
    {
        [Header("Avatar Configuration")]
        [SerializeField] private AvatarConfig avatarConfig;

        public AvatarConfig Config => avatarConfig;

        private void Awake()
        {
            if (avatarConfig == null)
            {
                Debug.LogWarning($"{nameof(AvatarConfigReference)} on {gameObject.name} has no AvatarConfig assigned!", this);
            }
        }
    }
}