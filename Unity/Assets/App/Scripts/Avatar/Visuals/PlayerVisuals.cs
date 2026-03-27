using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Mapping;
using Application.Scripts.Experiment;
using Application.Scripts.ScriptableObjects;
using Fusion;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Avatar.Visuals
{
    public class PlayerVisuals : MonoBehaviour
    {
        [SerializeField] private AvatarScriptableObject avatar;
        [SerializeField] private AvatarDriver avatarDriver;
        [SerializeField] private Application.Scripts.Avatar.Utils.AvatarConfigReference avatarConfigReference;
        [SerializeField] private Transform hmdCameraTransform;
        [SerializeField] private AvatarVisibility avatarVisibility;
        [SerializeField] private UnityEvent<AvatarBoneReference> avatarInitialized;

        [SerializeField][HideInInspector] private AvatarScriptableObject[] _availableAvatars;

        private GameObject _avatarInstance;
        private AvatarBoneReference _boneRef;
        private NetworkObject _networkObject;
        private Transform _visualsContainer;

        public AvatarScriptableObject Avatar
        {
            get => avatar;
            set { avatar = value; SetupAvatar(); }
        }

        private void Awake()
        {
            _networkObject = GetComponent<NetworkObject>();
            _availableAvatars = Resources.LoadAll<AvatarScriptableObject>("Avatars");
            if (_availableAvatars.Length > 0) avatar = _availableAvatars[0];
        }

        private void OnEnable()
        {
            SetupAvatar();
            ExperimentController.OnChangeGender += SetGender;
            SetAvatarVisibility(avatarVisibility);
        }

        private void OnDisable()
        {
            ExperimentController.OnChangeGender -= SetGender;
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

            if (avatar == null) return;

            _avatarInstance = Instantiate(avatar.AvatarGo, _visualsContainer);
            _avatarInstance.layer = 10; // AvatarBody layer

            _boneRef = AvatarBoneReference.Build(avatar, _avatarInstance);

            float verticalOffset = 0f;
            if (hmdCameraTransform != null)
                verticalOffset = AvatarRetargeting.Calibrate(_boneRef.Root, _boneRef.Head, hmdCameraTransform.position);

            if (avatarDriver != null && avatarConfigReference?.Config != null)
                avatarDriver.Initialize(_boneRef, avatarConfigReference.Config, verticalOffset);

            Debug.Log($"<color=#ADD8E6>[Avatar]</color> Avatar swapped to {avatar.name}");
            avatarInitialized?.Invoke(_boneRef);

            SetAvatarVisibility(avatarVisibility);
        }

        public void SetAvatarVisibility(AvatarVisibility visibility)
        {
            if (_avatarInstance == null) return;
            _avatarInstance.SetActive(visibility == AvatarVisibility.AVATAR);
        }

        private void SetGender(int playerId, Gender gender)
        {
            if (_networkObject == null || _networkObject.InputAuthority.IsNone) return;
            if (_networkObject.InputAuthority.PlayerId != playerId) return;

            foreach (AvatarScriptableObject a in _availableAvatars)
            {
                if (a.Gender == gender)
                {
                    Avatar = a;
                    break;
                }
            }
        }
    }
}
