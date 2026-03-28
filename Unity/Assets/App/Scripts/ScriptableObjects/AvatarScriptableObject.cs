using Application.Scripts.Avatar;
using AYellowpaper.SerializedCollections;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Application.Scripts.ScriptableObjects
{
    [CreateAssetMenu(fileName = "AvatarData", menuName = "ManualStudy/AvatarData", order = 1)]
    public class AvatarScriptableObject : ScriptableObject
    {
        [SerializeField] private Gender gender;
        [SerializeField] private GameObject avatarGO;

        [SerializeField] private Animator animator;
        [SerializeField] private UnityEngine.Avatar avatarSkeleton;

        [SerializedDictionary("Human Bone", "Transform")]
        [SerializeField] private SerializedDictionary<string, Transform> skeleton;
        public Gender Gender => gender;
        public GameObject AvatarGo => avatarGO;
        public Animator Animator => animator;
        public UnityEngine.Avatar AvatarSkeleton => avatarSkeleton;
        
        [ContextMenu("Setup Bones")]
        private void SetupBones()
        {
            if (animator == null || animator.avatar == null)
            {
                animator = avatarGO.GetComponentInChildren<Animator>();
#if UNITY_EDITOR
                avatarSkeleton = ExtractAvatar(avatarGO);
#endif
                animator.avatar = avatarSkeleton;
            }

            skeleton = new SerializedDictionary<string, Transform>();
            
            foreach (var t in animator.avatar.humanDescription.human)
            {
                skeleton[t.humanName] = avatarGO.transform.FindRecursive(t.boneName);
            }
        }

        public Transform TryGetBone(HumanBodyBones bone)
        {
            return skeleton[bone.ToString()];
        }
#if UNITY_EDITOR
        public UnityEngine.Avatar ExtractAvatar(GameObject avatarGameObject)
        {
            string path = AssetDatabase.GetAssetPath(avatarGameObject);
            UnityEngine.Avatar avatar = AssetDatabase.LoadAssetAtPath<UnityEngine.Avatar>(path);

            return avatar;
        }
#endif
    }
}
