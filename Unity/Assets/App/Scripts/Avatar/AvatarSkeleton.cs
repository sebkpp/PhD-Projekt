using AnimationRigging;
using Application.Scripts.Avatar.Hand;
using AYellowpaper.SerializedCollections;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using UnityEngine.Animations.Rigging;
using VRHands.Attributes;

namespace Application.Scripts.Avatar
{
    [System.Serializable]
    public class HandSkeleton
    {
        public Transform hand;
        [SerializeField] [ReadOnly] private Vector3 position;
        [SerializeField] [ReadOnly] private Vector3 rotation;

        public FingerSkeleton thumb = new();
        public FingerSkeleton index = new();
        public FingerSkeleton middle = new();
        public FingerSkeleton ring = new();
        public FingerSkeleton little = new();

        private HandTransformData _handState;

        public HandTransformData HandState
        {
            get
            {
                // position = hand.position;
                // rotation = hand.rotation.eulerAngles;

                // _handState.handPosition = hand.localPosition;
                // _handState.handRotation = hand.localRotation;

                _handState.index = index.FingerState;
                _handState.thumb = thumb.FingerState;
                _handState.middle = middle.FingerState;
                _handState.ring = ring.FingerState;
                _handState.pinky = little.FingerState;

                return _handState;
            }

            set
            {
                thumb.FingerState = value.thumb;
                index.FingerState = value.index;
                ring.FingerState = value.ring;
                middle.FingerState = value.middle;
                little.FingerState = value.pinky;

                // position = value.handPosition;
                // rotation = value.handRotation.eulerAngles;
                //
                // hand.localPosition = position;
                // hand.localRotation = value.handRotation;
            }
        }
    }

    [System.Serializable]
    public class FingerSkeleton
    {
        public FingerJoint metacarpal = new();
        public FingerJoint proximal = new();
        public FingerJoint intermediate = new();
        public FingerJoint distal = new();

        private FingerTransformData _fingerState;

        public FingerTransformData FingerState
        {
            get
            {
                _fingerState.metacarpal = metacarpal.FingerJointTransformData;
                _fingerState.proximal = proximal.FingerJointTransformData;
                _fingerState.intermediate = intermediate.FingerJointTransformData;
                _fingerState.distal = distal.FingerJointTransformData;

                return _fingerState;
            }

            set
            {
                metacarpal.FingerJointTransformData = value.metacarpal;
                proximal.FingerJointTransformData = value.proximal;
                intermediate.FingerJointTransformData = value.intermediate;
                distal.FingerJointTransformData = value.distal;
            }
        }
    }

    [System.Serializable]
    public class FingerJoint
    {
        public Transform transform;

        [SerializeField] [ReadOnly] private Vector3 position;
        [SerializeField] [ReadOnly] private Vector3 rotation;

        public FingerJointTransformData FingerJointTransformData
        {
            get
            {
                FingerJointTransformData jointTransformData = new FingerJointTransformData();

                if (!transform) return jointTransformData;

                // Position
                position = transform.position;
                Vector3 localPosition = transform.localPosition;
                jointTransformData.position = localPosition;

                // Rotation
                Quaternion rotationCache = transform.rotation;
                Quaternion localRotation = transform.localRotation;
                rotation = rotationCache.eulerAngles;
                jointTransformData.rotation = localRotation;

                return jointTransformData;
            }

            set
            {
                if (!transform) return;

                position = value.position;
                rotation = value.rotation.eulerAngles;

                transform.localPosition = value.position;
                transform.localRotation = value.rotation;
            }
        }
    }

    public class AvatarSkeleton : MonoBehaviour
    {
        [SerializeField] private Transform skeletonRoot;

        // Stores the instantiated avatar skeleton/armatur
        [SerializeField] private SerializedDictionary<string, Transform> skeleton;

        [SerializeField] private Transform headIKTarget;
        [SerializeField] private HandSkeleton leftHandIKTarget;
        [SerializeField] private HandSkeleton rightHandIKTarget;

        public Transform SkeletonRoot
        {
            get => skeletonRoot;
            set => skeletonRoot = value;
        }

        public Transform HeadIKTarget => headIKTarget;

        public HandSkeleton LeftHandIKTarget => leftHandIKTarget;

        public HandSkeleton RightHandIKTarget => rightHandIKTarget;


        /// <summary>
        /// Return transform from given Bone
        /// </summary>
        /// <param name="bone"></param>
        /// <returns></returns>
        public Transform TryGetBone(HumanBodyBones bone)
        {
            return skeleton[bone.ToString()];
        }

        /// <summary>
        /// Return transform from given Bone
        /// </summary>
        /// <param name="bone"></param>
        /// <returns></returns>
        public Transform TryGetBone(string bone)
        {
            return skeleton[bone];
        }


        /// <summary>
        /// Initialize Skeleton information and set IK-Constrains
        /// ToDo: Moving IK-Constrains setup in its own class?
        /// </summary>
        /// <param name="humanDescription"></param>
        public void InitAvatar(HumanDescription humanDescription)
        {
            if (skeletonRoot == null)
            {
                Debug.LogWarning("Skeleton Root is not set");
                return;
            }

            // Reads the skeleton/armatur from avatars rigging
            skeleton = new SerializedDictionary<string, Transform>();
            foreach (HumanBone humanBone in humanDescription.human)
            {
                skeleton[humanBone.humanName] = SkeletonRoot.transform.FindRecursive(humanBone.boneName);
            }

#if UNITY_EDITOR
            // To visualize the rigged bones
            AnimationRigController.BoneRendererSetup(transform);
#endif

            // Building the Rig and Constrains
            RigBuilder rigBuilder = AnimationRigController.RigBuilderSetup(transform);
            Rig constrains = AnimationRigController.RigSetup(rigBuilder, transform, "Constrains");

            // Constrains for Head and Arms/Hand
            SetupConstrains(constrains);

            rigBuilder.Build(); // Lets the avatar get a weird pose
        }

        private void SetupConstrains(Rig rigConstrains)
        {
            headIKTarget = SetupHeadConstrain(rigConstrains);
            SetupUpperBody(rigConstrains, headIKTarget);
            
            leftHandIKTarget = SetupHand(rigConstrains, skeleton[HumanBodyBones.LeftHand.ToString()], "LeftHandIK");
            rightHandIKTarget = SetupHand(rigConstrains, skeleton[HumanBodyBones.RightHand.ToString()], "RightHandIK");
        }


        private Transform SetupHeadConstrain(Rig constrain)
        {
            GameObject head = new GameObject("HeadEyeCenter", typeof(MultiAimConstraint));
            head.transform.SetParent(constrain.transform);
            Transform constrainedHead = skeleton[HumanBodyBones.Head.ToString()];

            GameObject target = new GameObject("Target");
            target.transform.SetParent(head.transform);

            Transform rightEye = TryGetBone(HumanBodyBones.RightEye);
            Transform leftEye = TryGetBone(HumanBodyBones.LeftEye);
            
            GameObject centerEyeAvatar = new GameObject("CenterEye");
            centerEyeAvatar.transform.SetParent(constrainedHead);
            centerEyeAvatar.transform.SetPositionAndRotation(Vector3.Lerp(rightEye.position, leftEye.position, 0.5f),
                Quaternion.identity);
            
            head.transform.SetPositionAndRotation(centerEyeAvatar.transform.position,
                centerEyeAvatar.transform.rotation);
            skeleton.Add("CenterEye", centerEyeAvatar.transform);
            
            // // Setup Constrain
            WeightedTransformArray sourceObjects = new WeightedTransformArray(0)
            {
                new WeightedTransform(target.transform, 1)
            };
            
            MultiAimConstraint headConstrain = head.GetComponent<MultiAimConstraint>();
            
            // head.GetComponent<RotationHelper>().SetConstrains(constrainedHead, centerEyeAvatar.transform);
            
            headConstrain.data.constrainedObject = constrainedHead.transform;
            headConstrain.data.sourceObjects = sourceObjects;
             headConstrain.data.aimAxis = MultiAimConstraintData.Axis.Y;
             headConstrain.data.upAxis = MultiAimConstraintData.Axis.X_NEG;
             headConstrain.data.constrainedXAxis = true;
             headConstrain.data.constrainedYAxis = true;
             headConstrain.data.constrainedZAxis = true;
             
             headConstrain.data.maintainOffset = false;
             headConstrain.data.limits = new Vector2(-90, 90);
             headConstrain.data.offset = new Vector3(0, 0, -60);

             //headConstrain.data.worldUpType = MultiAimConstraintData.WorldUpType.SceneUp;
            
            
             // GameObject centerEye = new GameObject("HeadEyeCenter", typeof(MultiReferentialConstraint));
             // centerEye.transform.SetParent(constrain.transform);


            // ToDo: Use to visual effectors later, effectors are not functional yet
            // RigEffectorData.Style style = new RigEffectorData.Style
            // {
            //     color = new Color(0.5f,0,0.5f,0.2f),
            //     size =  0.2f,
            // };
            //
            // constrain.AddEffector(target.transform, style);

            return target.transform;
        }

        public void SetupUpperBody(Rig constrain, Transform headTarget)
        {
            GameObject upperBody = new GameObject("Chest", typeof(MultiParentConstraint));
            upperBody.transform.SetParent(constrain.transform);
            Transform constrainedUpperBody = skeleton[HumanBodyBones.UpperChest.ToString()];
            
            upperBody.transform.SetPositionAndRotation(constrainedUpperBody.transform.position,
                constrainedUpperBody.transform.rotation);
            
            
            // Setup Constrain
            MultiParentConstraint upperBodyConstrain = upperBody.GetComponent<MultiParentConstraint>();
            upperBodyConstrain.data.constrainedObject = constrainedUpperBody;
            
            WeightedTransformArray sourceObjects = new WeightedTransformArray(0)
            {
                new WeightedTransform(headTarget.transform, 0.2f)
            };
            
            upperBodyConstrain.data.sourceObjects = sourceObjects;

            upperBodyConstrain.data.maintainRotationOffset = true;
            upperBodyConstrain.data.maintainPositionOffset = true;

            upperBodyConstrain.data.constrainedPositionXAxis = true;
            upperBodyConstrain.data.constrainedPositionYAxis = true;
            upperBodyConstrain.data.constrainedPositionZAxis = true;

            upperBodyConstrain.data.constrainedRotationXAxis = true;
            upperBodyConstrain.data.constrainedRotationYAxis = true;
            upperBodyConstrain.data.constrainedRotationZAxis = true;
        }

        public HandSkeleton SetupHand(Rig constrain, Transform handTransform, string handName)
        {
            HandSkeleton hand = new HandSkeleton();
            GameObject handIK = new GameObject(handName, typeof(TwoBoneIKConstraint));
            handIK.transform.SetParent(constrain.transform);
            GameObject target = new GameObject("Target");
            target.transform.SetParent(handIK.transform);
            target.transform.SetPositionAndRotation(handTransform.position, handTransform.rotation);

            GameObject handHint = new GameObject($"Hint");
            handHint.transform.SetParent(handIK.transform);

            Transform foreArm = handTransform.parent;
            Transform upperArm = foreArm.parent;

            handHint.transform.SetPositionAndRotation(foreArm.position, foreArm.rotation);

            // Move hint a bit in elbow movement direction
            handHint.transform.position += handHint.transform.rotation * transform.up * 0.1f;

            TwoBoneIKConstraint armConstrain = handIK.GetComponent<TwoBoneIKConstraint>();

            armConstrain.data.target = target.transform;
            armConstrain.data.hint = handHint.transform;

            armConstrain.data.tip = handTransform;
            armConstrain.data.mid = foreArm;
            armConstrain.data.root = upperArm;
            armConstrain.data.hintWeight = 1f;
            armConstrain.data.targetPositionWeight = 1f;
            armConstrain.data.targetRotationWeight = 1f;

            SetupArmTwists(constrain, target.transform, handTransform);
            SetupFingers(target.transform, ref hand, handName);

            hand.hand = target.transform;
            return hand;
        }

        private void SetupArmTwists(Rig constrain, Transform handTarget, Transform hand)
        {
            Transform foreArm = hand.transform.parent;
            Transform upperArm = foreArm.transform.parent;

            SetupArmTwist(constrain, handTarget, foreArm, "ForeArm", 0.8f);
            SetupArmTwist(constrain, handTarget, upperArm, "UpperArm", 0.1f);

        }

        private void SetupArmTwist(Rig constrain, Transform handTarget, Transform constrainedArm, string twistName,  
            float weight)
        {
            GameObject upperArmTwist = new GameObject(twistName, typeof(MultiRotationConstraint));
            upperArmTwist.transform.SetParent(constrain.transform);
            MultiRotationConstraint upperArmTwistConstrain = upperArmTwist.GetComponent<MultiRotationConstraint>();
            
            WeightedTransformArray sourceObjects = new WeightedTransformArray(0)
            {
                new WeightedTransform(handTarget.transform, weight)
            };
            
            upperArmTwistConstrain.data.constrainedObject = constrainedArm;
            upperArmTwistConstrain.data.constrainedXAxis = true;
            upperArmTwistConstrain.data.maintainOffset = true;
            upperArmTwistConstrain.data.sourceObjects = sourceObjects;
        }

        private void SetupFingers(Transform handTransform, ref HandSkeleton handSkeleton, string handName)
        {
            string isLeft = handName.Contains("Left") ? "Left" : "Right";

            SetupFinger("Thumb", handTransform, ref handSkeleton.thumb, isLeft);
            SetupFinger("Index", handTransform, ref handSkeleton.index, isLeft);
            SetupFinger("Middle", handTransform, ref handSkeleton.middle, isLeft);
            SetupFinger("Ring", handTransform, ref handSkeleton.ring, isLeft);
            SetupFinger("Little", handTransform, ref handSkeleton.little, isLeft);
        }

        private void SetupFinger(string fingerName, Transform parent, ref FingerSkeleton handSkeleton,
            string handedness)
        {
            string proximalName = $"{handedness} {fingerName} Proximal";
            handSkeleton.proximal.transform = SetupPhalanx(proximalName, parent);

            string intermediateName = $"{handedness} {fingerName} Intermediate";
            handSkeleton.intermediate.transform = SetupPhalanx(intermediateName, handSkeleton.proximal.transform);

            string distalName = $"{handedness} {fingerName} Distal";
            handSkeleton.distal.transform = SetupPhalanx(distalName, handSkeleton.intermediate.transform);
        }

        private Transform SetupPhalanx(string fingerBoneName, Transform parent)
        {
            Transform constrainedObject = skeleton[fingerBoneName];

            GameObject finger = new GameObject(fingerBoneName, typeof(OverrideTransform));
            finger.transform.SetParent(parent);
            finger.transform.SetPositionAndRotation(constrainedObject.position, constrainedObject.rotation);

            GameObject fingerTarget = new GameObject($"{finger.name}_target");
            fingerTarget.transform.SetParent(finger.transform);
            fingerTarget.transform.SetPositionAndRotation(constrainedObject.position, constrainedObject.rotation);

            OverrideTransform fingerConstrain = finger.GetComponent<OverrideTransform>();
            fingerConstrain.data.constrainedObject = constrainedObject;
            fingerConstrain.data.sourceObject = fingerTarget.transform;
            fingerConstrain.data.space = OverrideTransformData.Space.Pivot;
            fingerConstrain.data.positionWeight = 0;
            fingerConstrain.data.rotationWeight = 1;

            return fingerTarget.transform;
        }
    }
}