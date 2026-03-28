using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Mapping;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Experiment;
using Application.Scripts.Network.Input;
using Application.Scripts.Avatar;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Avatar.Visuals
{
    public class PlayerVisuals : MonoBehaviour
    {
        [SerializeField] private AvatarSet _avatarSet;
        [SerializeField] private AvatarDriver _avatarDriver;
        [SerializeField] private AvatarConfigReference _avatarConfigReference;
        [SerializeField] private Transform _hmdCameraTransform;
        [SerializeField] private AvatarVisibility _avatarVisibility;
        [SerializeField] private UnityEvent<AvatarBoneReference> _avatarInitialized;

        private string _gender = "Female"; // default until SetGender is called
        private GameObject _avatarInstance;
        private AvatarBoneReference _boneRef;
        private Transform _visualsContainer;

        public void SetGender(string gender)
        {
            _gender = gender;
            if (_visualsContainer != null)
                SwapAvatar();
        }

        private void Awake()
        {
        }

        private void OnEnable()
        {
            SetupAvatar();
            SetAvatarVisibility(_avatarVisibility);
        }

        private void OnValidate()
        {
            SetAvatarVisibility(_avatarVisibility);
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

            if (_avatarSet == null) return;

            GameObject prefab = _avatarSet.GetPrefab(_gender);
            if (prefab == null) return;

            _avatarInstance = Instantiate(prefab, _visualsContainer);
            _avatarInstance.layer = 10; // AvatarBody layer

            _boneRef = AvatarBoneReference.Build(_avatarInstance);
            if (_boneRef == null) return;

            float verticalOffset = 0f;
            if (_hmdCameraTransform != null)
                verticalOffset = AvatarRetargeting.Calibrate(_boneRef.Root, _boneRef.Head, _hmdCameraTransform.position);

            if (_avatarDriver != null && _avatarConfigReference?.Config != null)
                _avatarDriver.Initialize(_boneRef, _avatarConfigReference.Config, verticalOffset);

            foreach (NetworkHand nh in GetComponentsInChildren<NetworkHand>(includeInactive: true))
            {
                bool isLeft = nh.Side == RigPart.LeftController;
                nh.AvatarHand = isLeft ? _boneRef.LeftHand : _boneRef.RightHand;
            }

            Debug.Log($"<color=#ADD8E6>[Avatar]</color> Avatar swapped: {prefab.name} ({_gender})");
            _avatarInitialized?.Invoke(_boneRef);
            SetAvatarVisibility(_avatarVisibility);
        }

        public void SetAvatarVisibility(AvatarVisibility visibility)
        {
            if (_avatarInstance == null) return;
            _avatarInstance.SetActive(visibility == AvatarVisibility.AVATAR);
        }
    }
}
