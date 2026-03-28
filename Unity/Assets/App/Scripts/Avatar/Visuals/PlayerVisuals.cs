using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Mapping;
using Application.Scripts.Network.Input;
using Application.Scripts.Avatar;
using Fusion;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Avatar.Visuals
{
    public class PlayerVisuals : MonoBehaviour
    {
        [SerializeField] private AvatarSet avatarSet;
        [SerializeField] private AvatarDriver avatarDriver;
        [SerializeField] private Application.Scripts.Avatar.Utils.AvatarConfigReference avatarConfigReference;
        [SerializeField] private Transform hmdCameraTransform;
        [SerializeField] private AvatarVisibility avatarVisibility;
        [SerializeField] private UnityEvent<AvatarBoneReference> avatarInitialized;

        private string _gender = "Female"; // default until SetGender is called
        private GameObject _avatarInstance;
        private AvatarBoneReference _boneRef;
        private NetworkObject _networkObject;
        private Transform _visualsContainer;

        public void SetGender(string gender)
        {
            _gender = gender;
            if (_visualsContainer != null)
                SwapAvatar();
        }

        private void Awake()
        {
            _networkObject = GetComponent<NetworkObject>();
        }

        private void OnEnable()
        {
            SetupAvatar();
            SetAvatarVisibility(avatarVisibility);
        }

        private void OnValidate()
        {
            SetAvatarVisibility(avatarVisibility);
        }

        private void SetupAvatar()
        {
            if (_visualsContainer == null)
            {
                _visualsContainer = new GameObject("AvatarVisuals").transform;
                _visualsContainer.SetParent(transform);
                _visualsContainer.localPosition = Vector3.zero;
                _visualsContainer.localRotation = Quaternion.identity;
            }
            SwapAvatar();
        }

        private void SwapAvatar()
        {
            for (int i = _visualsContainer.childCount - 1; i >= 0; i--)
            {
#if UNITY_EDITOR
                DestroyImmediate(_visualsContainer.GetChild(i).gameObject);
#else
                Destroy(_visualsContainer.GetChild(i).gameObject);
#endif
            }

            if (avatarSet == null) return;

            GameObject prefab = avatarSet.GetPrefab(_gender);
            if (prefab == null) return;

            _avatarInstance = Instantiate(prefab, _visualsContainer);
            _avatarInstance.layer = 10; // AvatarBody layer

            _boneRef = AvatarBoneReference.Build(_avatarInstance);
            if (_boneRef == null) return;

            float verticalOffset = 0f;
            if (hmdCameraTransform != null)
                verticalOffset = AvatarRetargeting.Calibrate(_boneRef.Root, _boneRef.Head, hmdCameraTransform.position);

            if (avatarDriver != null && avatarConfigReference?.Config != null)
                avatarDriver.Initialize(_boneRef, avatarConfigReference.Config, verticalOffset);

            foreach (NetworkHand nh in GetComponentsInChildren<NetworkHand>(includeInactive: true))
            {
                bool isLeft = nh.Side == RigPart.LeftController;
                nh.AvatarHand = isLeft ? _boneRef.LeftHand : _boneRef.RightHand;
            }

            Debug.Log($"<color=#ADD8E6>[Avatar]</color> Avatar swapped: {prefab.name} ({_gender})");
            avatarInitialized?.Invoke(_boneRef);
            SetAvatarVisibility(avatarVisibility);
        }

        public void SetAvatarVisibility(AvatarVisibility visibility)
        {
            if (_avatarInstance == null) return;
            _avatarInstance.SetActive(visibility == AvatarVisibility.AVATAR);
        }
    }
}
