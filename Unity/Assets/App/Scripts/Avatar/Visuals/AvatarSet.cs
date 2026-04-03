using UnityEngine;

namespace Application.Scripts.Avatar.Visuals
{
    [CreateAssetMenu(fileName = "AvatarSet", menuName = "ManualStudy/AvatarSet")]
    public class AvatarSet : ScriptableObject
    {
        [SerializeField] private GameObject _malePrefab;
        [SerializeField] private GameObject _femalePrefab;

        public GameObject MalePrefab   { get => _malePrefab;   set => _malePrefab   = value; }
        public GameObject FemalePrefab { get => _femalePrefab; set => _femalePrefab = value; }

        public GameObject GetPrefab(string gender)
            => gender == "Male" ? _malePrefab : _femalePrefab;
    }
}
