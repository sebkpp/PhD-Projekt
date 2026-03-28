using Application.Scripts.ScriptableObjects;
using UnityEngine;

namespace Application.Scripts.Avatar.Driver
{
    /// <summary>
    /// Finger index constants for the FingerBones array.
    /// </summary>
    public static class FingerIndex
    {
        public const int Thumb  = 0;
        public const int Index  = 1;
        public const int Middle = 2;
        public const int Ring   = 3;
        public const int Pinky  = 4;
    }

    /// <summary>
    /// Joint index constants within one finger in the FingerBones array.
    /// Maps to Rocketbox Biped naming: Joint 0 = Finger0/1/2/3/4 (metacarpal/base),
    /// Joint 1 = Finger01/11/21/31/41 (proximal), Joint 2 = Finger02/12/22/32/42.
    /// Note: Unity humanoid labels these as Proximal/Intermediate/Distal but they
    /// correspond to OpenXR Metacarpal/Proximal/Intermediate respectively.
    /// </summary>
    public static class JointIndex
    {
        public const int Metacarpal   = 0; // Unity "Proximal"   = Biped Finger0
        public const int Proximal     = 1; // Unity "Intermediate" = Biped Finger01
        public const int Intermediate = 2; // Unity "Distal"     = Biped Finger02
    }

    /// <summary>
    /// Pure data container holding direct Transform references to all avatar bones needed
    /// by AvatarDriver.  No MonoBehaviour, no constraint setup.
    /// Build via <see cref="Build"/> after avatar instantiation.
    /// </summary>
    public class AvatarBoneReference
    {
        public Transform Root;
        public Transform Head;

        // Arms — Left
        public Transform LeftUpperArm;
        public Transform LeftForearm;
        public Transform LeftForearmTwist;  // virtual bone, set by AvatarDriver.InsertVirtualTwistBones()
        public Transform LeftHand;

        // Arms — Right
        public Transform RightUpperArm;
        public Transform RightForearm;
        public Transform RightForearmTwist; // virtual bone, set by AvatarDriver.InsertVirtualTwistBones()
        public Transform RightHand;

        /// <summary>
        /// Finger bones[side, finger, joint].
        /// side: 0 = left, 1 = right.
        /// finger: use <see cref="FingerIndex"/> constants.
        /// joint: use <see cref="JointIndex"/> constants.
        /// </summary>
        public Transform[,,] FingerBones = new Transform[2, 5, 3];

        /// <summary>
        /// Builds an AvatarBoneReference from the avatar's Animator.
        /// The avatar GameObject must have a Unity Humanoid Avatar configured.
        /// </summary>
        public static AvatarBoneReference Build(AvatarScriptableObject avatarAsset, GameObject avatarInstance)
        {
            Animator animator = avatarInstance.GetComponentInChildren<Animator>();

            if (animator == null)
            {
                Debug.LogError($"[AvatarBoneReference] No Animator found on '{avatarInstance.name}'. The avatar prefab must have a Humanoid Animator.");
                return null;
            }

            var r = new AvatarBoneReference
            {
                Root         = avatarInstance.transform,
                Head         = animator.GetBoneTransform(HumanBodyBones.Head),
                LeftUpperArm = animator.GetBoneTransform(HumanBodyBones.LeftUpperArm),
                LeftForearm  = animator.GetBoneTransform(HumanBodyBones.LeftLowerArm),
                LeftHand     = animator.GetBoneTransform(HumanBodyBones.LeftHand),
                RightUpperArm = animator.GetBoneTransform(HumanBodyBones.RightUpperArm),
                RightForearm  = animator.GetBoneTransform(HumanBodyBones.RightLowerArm),
                RightHand     = animator.GetBoneTransform(HumanBodyBones.RightHand),
            };

            // Left fingers — Unity "Proximal" = Biped first bone = OpenXR Metacarpal
            r.FingerBones[0, FingerIndex.Thumb,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.LeftThumbProximal);
            r.FingerBones[0, FingerIndex.Thumb,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.LeftThumbIntermediate);
            r.FingerBones[0, FingerIndex.Thumb,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.LeftThumbDistal);

            r.FingerBones[0, FingerIndex.Index,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.LeftIndexProximal);
            r.FingerBones[0, FingerIndex.Index,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.LeftIndexIntermediate);
            r.FingerBones[0, FingerIndex.Index,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.LeftIndexDistal);

            r.FingerBones[0, FingerIndex.Middle, JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.LeftMiddleProximal);
            r.FingerBones[0, FingerIndex.Middle, JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.LeftMiddleIntermediate);
            r.FingerBones[0, FingerIndex.Middle, JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.LeftMiddleDistal);

            r.FingerBones[0, FingerIndex.Ring,   JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.LeftRingProximal);
            r.FingerBones[0, FingerIndex.Ring,   JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.LeftRingIntermediate);
            r.FingerBones[0, FingerIndex.Ring,   JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.LeftRingDistal);

            r.FingerBones[0, FingerIndex.Pinky,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.LeftLittleProximal);
            r.FingerBones[0, FingerIndex.Pinky,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.LeftLittleIntermediate);
            r.FingerBones[0, FingerIndex.Pinky,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.LeftLittleDistal);

            // Right fingers
            r.FingerBones[1, FingerIndex.Thumb,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.RightThumbProximal);
            r.FingerBones[1, FingerIndex.Thumb,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.RightThumbIntermediate);
            r.FingerBones[1, FingerIndex.Thumb,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.RightThumbDistal);

            r.FingerBones[1, FingerIndex.Index,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.RightIndexProximal);
            r.FingerBones[1, FingerIndex.Index,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.RightIndexIntermediate);
            r.FingerBones[1, FingerIndex.Index,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.RightIndexDistal);

            r.FingerBones[1, FingerIndex.Middle, JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.RightMiddleProximal);
            r.FingerBones[1, FingerIndex.Middle, JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.RightMiddleIntermediate);
            r.FingerBones[1, FingerIndex.Middle, JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.RightMiddleDistal);

            r.FingerBones[1, FingerIndex.Ring,   JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.RightRingProximal);
            r.FingerBones[1, FingerIndex.Ring,   JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.RightRingIntermediate);
            r.FingerBones[1, FingerIndex.Ring,   JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.RightRingDistal);

            r.FingerBones[1, FingerIndex.Pinky,  JointIndex.Metacarpal]   = animator.GetBoneTransform(HumanBodyBones.RightLittleProximal);
            r.FingerBones[1, FingerIndex.Pinky,  JointIndex.Proximal]     = animator.GetBoneTransform(HumanBodyBones.RightLittleIntermediate);
            r.FingerBones[1, FingerIndex.Pinky,  JointIndex.Intermediate] = animator.GetBoneTransform(HumanBodyBones.RightLittleDistal);

            return r;
        }
    }
}
