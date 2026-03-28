using UnityEngine;

namespace Application.Scripts.Avatar.Visuals
{
    [CreateAssetMenu(fileName = "AvatarSet", menuName = "ManualStudy/AvatarSet")]
    public class AvatarSet : ScriptableObject
    {
        [SerializeField] public GameObject malePrefab;
        [SerializeField] public GameObject femalePrefab;

        public GameObject GetPrefab(string gender)
            => gender == "Male" ? malePrefab : femalePrefab;
    }
}
