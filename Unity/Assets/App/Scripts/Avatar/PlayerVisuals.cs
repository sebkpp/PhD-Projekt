using System;
using Application.Scripts.Utils.Extensions;
using Application.Scripts.Experiment;
using Application.Scripts.ScriptableObjects;
using Fusion;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Avatar
{
    [RequireComponent(typeof(AvatarMapping))]
    public class PlayerVisuals : MonoBehaviour
    {
        //Inspector private
        [SerializeField] private SkinnedMeshRenderer handMeshRenderer;
        [SerializeField] private AvatarScriptableObject avatar;
        [SerializeField] private UnityEvent<AvatarSkeleton> avatarInitialized;
        [SerializeField][HideInInspector] private AvatarScriptableObject[] availableAvatars;

        [SerializeField] private AvatarVisibility avatarVisibility;
        
        //private
        private GameObject _avatar;
        private AvatarSkeleton _skeleton;
        private AvatarMapping _mapping;
        private NetworkObject _networkObject;

        
        #region PROPERTIES
        
        public AvatarScriptableObject Avatar
        {
            get => avatar;
            set
            {
                avatar = value;
                SetupAvatar();
            }
        }
        
        #endregion
        
        #region setup 
        private void Awake()
        {
            _networkObject = GetComponent<NetworkObject>();
            _mapping = GetComponent<AvatarMapping>();

            availableAvatars = Resources.LoadAll<AvatarScriptableObject>("Avatars");

            if (availableAvatars.Length > 0)
            {
                avatar = availableAvatars[0];
            }
        }
        private void OnEnable()
        {
            SetupAvatar();

            ExperimentController.OnChangeGender += SetGender;
            ExperimentController.OnChangeAvatarOptions += SetAvatarOptions;
            //TODO Change hand visuals in experiment

            //Start state
            // SetAvatarOptions(-1, AvatarOptions.Hands);
            SetAvatarVisibility(avatarVisibility);

        }

        private void OnValidate()
        {
            SetAvatarVisibility(avatarVisibility);
        }

        private void SetupAvatar()
        {
            // Setup Visuals Container
            Transform visualsContainer = _mapping.Visuals ?? CreateVisualsContainer();

            _mapping.Visuals = visualsContainer;

            CreateAvatar(visualsContainer);
        }

        private void CreateAvatar(Transform visualsContainer)
        {
            // Clear any present avatar before creating a new one
            if (visualsContainer.childCount != 0)
            {
                ClearVisuals(visualsContainer);
            }

            if (avatar == null) return;

            // Instantiate new Avatar-GameObject within visualContainer
            _avatar = Instantiate(avatar.AvatarGo, visualsContainer);
            _avatar.layer = 10; //AvatarBody layer

            _skeleton = _avatar.AddComponent<AvatarSkeleton>();
            _skeleton.SkeletonRoot = _avatar.transform;
            _skeleton.InitAvatar(avatar.AvatarSkeleton.humanDescription);

            Debug.Log($"<color=#ADD8E6>[Avatar]</color> Avatar instantiated!");
            avatarInitialized?.Invoke(_skeleton);
        }

        private Transform CreateVisualsContainer()
        {
            var container = new GameObject("AvatarVisuals").transform;
            container.SetParent(transform);
            container.localPosition = Vector3.zero;
            container.localRotation = Quaternion.identity;
            return container;
        }

        private void ClearVisuals(Transform visualsContainer)
        {
#if UNITY_EDITOR || UNITY_EDITOR_64 || UNITY_EDITOR_WIN
            visualsContainer.DestroyChildrenImmediate();
#else
            visualsContainer.DestroyChildren();
#endif
        }

        #endregion

        public void SetAvatarVisibility(AvatarVisibility visibility)
        {
            if (!_avatar || !handMeshRenderer) return;
            
            switch (visibility)
            {
                case AvatarVisibility.AVATAR:
                    _avatar.SetActive(true);
                    handMeshRenderer.enabled = false;
                    break;
                case AvatarVisibility.HANDSONLY:
                    _avatar.SetActive(false);
                    handMeshRenderer.enabled = true;
                    break;
                case AvatarVisibility.INVISIBLE:
                    _avatar.SetActive(false);
                    handMeshRenderer.enabled = false;
                    break;
                default:
                    Debug.LogError("Avatar visibility is invalid!");
                    break;
            }
        }
        public void SetAvatarVisibility(bool visibility)
        {
            if (_avatar != null)
                _avatar.SetActive(visibility);

            if (handMeshRenderer != null)
                handMeshRenderer.enabled = visibility;
        }

        private void SetGender(int playerId, Gender gender)
        {
            if (_networkObject == null || _networkObject.InputAuthority.IsNone) return;
            if (_networkObject.InputAuthority.PlayerId != playerId) return;

            foreach (AvatarScriptableObject a in availableAvatars)
            {
                if (a.Gender == gender)
                {
                    avatar = a;
                    CreateAvatar(_mapping.Visuals);
                    break;
                }
            }
        }

        private void SetAvatarOptions(int id, AvatarOptions options)
        {
            bool onlyHands = options == AvatarOptions.Hands;

            if (handMeshRenderer != null)
                handMeshRenderer.enabled = onlyHands;

            if (avatar != null)
                _avatar.SetActive(!onlyHands);
        }
    }
}