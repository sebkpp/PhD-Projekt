using System.Collections;
using UtilsAvatarConfig = Application.Scripts.Avatar.Utils.AvatarConfig;
using UnityEngine;
using UnityEngine.Serialization;

namespace Application.Scripts.Avatar
{
    public class AvatarMapping : MonoBehaviour
    {
        [SerializeField] private UtilsAvatarConfig config;

        // [SerializeField] private float turnSmoothness;
        
        [FormerlySerializedAs("visuals")] [SerializeField] private Transform avatarVisualizationContainer;

        [SerializeField] private AvatarJointMap headMap;
        [SerializeField] private AvatarHandJointMap leftHandMap;
        [SerializeField] private AvatarHandJointMap rightHandMap;
        
        private AvatarSkeleton _skeleton;
        private bool _vrInitialized = false;
        public Transform Visuals
        {
            get => avatarVisualizationContainer;
            set => avatarVisualizationContainer = value;
        }

        /// <summary>
        /// Initialize and sets all IKTargets for Tracking by given AvatarSkeleton
        /// </summary>
        /// <param name="skeleton">The Avatar Skeleton</param>
        public void SetIKTargets(AvatarSkeleton skeleton)
        {
            _skeleton = skeleton;

            //SetHeadToVRHeadPosition();

            headMap.SetIKTarget(skeleton.HeadIKTarget);
            
            leftHandMap.SetIKTarget(skeleton.LeftHandIKTarget);
            rightHandMap.SetIKTarget(skeleton.RightHandIKTarget);
        }

        private void SetRotationOffsetToTransform(Transform t, Vector3 offset)
        {
            t.localRotation = Quaternion.Euler(offset);
        }

        private void Start()
        {
            StartCoroutine(CenterHeadPosition());
        }

        private IEnumerator CenterHeadPosition()
        {
            yield return new WaitForSeconds(1);

            SetHeadToVRHeadPosition();
        }


        private void FixedUpdate()
        {
            if (!_vrInitialized) return;
            
            MapAvatar();

            if (Input.GetKeyDown(KeyCode.R))
            {
                SetHeadToVRHeadPosition();
            }
        }


        private void MapAvatar()
        {
            if (_skeleton == null) return;
            
            // Head
            headMap.MapTarget(config.Head, Quaternion.identity);
            
            // Hands
            leftHandMap.MapTarget(config.LeftHand);
            rightHandMap.MapTarget(config.RightHand);
            
            // Legs
            SetRotationOffsetToTransform(_skeleton.TryGetBone(HumanBodyBones.LeftUpperLeg), config.LeftUpperLeg.rotation);
            SetRotationOffsetToTransform(_skeleton.TryGetBone(HumanBodyBones.LeftLowerLeg), config.LeftLowerLeg.rotation);

            SetRotationOffsetToTransform(_skeleton.TryGetBone(HumanBodyBones.RightUpperLeg), config.RightUpperLeg.rotation);
            SetRotationOffsetToTransform(_skeleton.TryGetBone(HumanBodyBones.RightLowerLeg), config.RightLowerLeg.rotation);
        }

        public void SetHeadToVRHeadPosition()
        {
            Debug.Log("Set Head To Camera Position");
            
            //Transform leftEye = _skeleton.TryGetBone(HumanBodyBones.LeftEye);
            //Transform rightEye = _skeleton.TryGetBone(HumanBodyBones.RightEye);
            Vector3 centerEyePosition = _skeleton.TryGetBone("CenterEye").position;
            
            //Vector3 centerEyePosition = Vector3.Lerp(leftEye.position, rightEye.position, 0.5f);
            //Vector3 avatarPosition = _skeleton.transform.position;
            Vector3 headPosition = headMap.VRSource.position;

            Vector3 offset = centerEyePosition - headPosition;
            _skeleton.transform.position -= offset;

            _vrInitialized = true;
        }
    }
}