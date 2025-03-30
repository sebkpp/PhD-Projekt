using UnityEngine;
using UnityEngine.Serialization;

namespace Application.Scripts.Avatar_rigging
{
    public class AvatarLookup : MonoBehaviour
    {
        [SerializeField] private Transform avatarRoot;
        [SerializeField] private Transform avatarHead;
        [SerializeField] private Transform avatarMiddleEye;
        [SerializeField] private Transform avatarFeet;

        public Transform AvatarFeet => avatarFeet;

        public Transform AvatarHead => avatarHead;

        public Transform AvatarRoot => avatarRoot;

        public Transform AvatarMiddleEye => avatarMiddleEye;
    }
}
