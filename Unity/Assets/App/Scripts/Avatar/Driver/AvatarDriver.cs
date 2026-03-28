using Application.Scripts.Interaction.States;
using UnityEngine;

namespace Application.Scripts.Avatar.Driver
{
    /// <summary>
    /// Caller-initiated bone driver — called from NetworkHand.Render each frame.
    /// Replaces AvatarMapping + AvatarSkeleton (Animation Rigging).
    ///
    /// Usage:
    ///   1. Call Initialize(boneRef, config) after avatar instantiation.
    ///   2. Call Apply(state) each frame (from LateUpdate or NetworkHand.Render).
    /// </summary>
    public class AvatarDriver : MonoBehaviour
    {
        [Header("Body smoothing")]
        [SerializeField] [Range(0f, 1f)] private float bodyYawSmoothing = 0.1f;

        private AvatarBoneReference _bones;
        private Application.Scripts.Avatar.Utils.AvatarConfig _config;
        private ArmBoneData _leftArm;
        private ArmBoneData _rightArm;
        private bool _initialized;

        private float _groundY; // avatar root Y after calibration, kept constant each frame
        private int _lastBodyDriveFrame = -1;

        // ------------------------------------------------------------------ //
        //  Initialization
        // ------------------------------------------------------------------ //

        /// <summary>
        /// Initializes the driver with fresh bone references.
        /// Must be called after every avatar swap (the new avatar has new Transform objects).
        /// Inserts virtual ForearmTwist bones and captures arm rest-pose data.
        /// </summary>
        public void Initialize(AvatarBoneReference bones, Application.Scripts.Avatar.Utils.AvatarConfig config, float verticalOffset = 0f)
        {
            _bones = bones;
            _config = config;

            InsertVirtualTwistBones();
            CaptureArmRestPose();

            _groundY = _bones.Root.position.y;
            _initialized = true;
        }

        private void InsertVirtualTwistBones()
        {
            _bones.LeftForearmTwist  = CreateTwistBone(_bones.LeftForearm,  _bones.LeftHand,  "L_ForearmTwist");
            _bones.RightForearmTwist = CreateTwistBone(_bones.RightForearm, _bones.RightHand, "R_ForearmTwist");
        }

        private static Transform CreateTwistBone(Transform forearm, Transform hand, string boneName)
        {
            var go = new GameObject(boneName);
            go.transform.SetParent(forearm);
            go.transform.SetPositionAndRotation(hand.position, hand.rotation);
            hand.SetParent(go.transform, worldPositionStays: true);
            return go.transform;
        }

        private void CaptureArmRestPose()
        {
            _leftArm = ArmBoneData.Build(
                _bones.LeftUpperArm, _bones.LeftForearm, _bones.LeftForearmTwist, _bones.LeftHand);
            _rightArm = ArmBoneData.Build(
                _bones.RightUpperArm, _bones.RightForearm, _bones.RightForearmTwist, _bones.RightHand);
        }

        // ------------------------------------------------------------------ //
        //  Per-frame application
        // ------------------------------------------------------------------ //

        /// <summary>
        /// Applies a full XRInputState to the avatar bones (head, body, both hands).
        /// </summary>
        public void Apply(XRInputState state)
        {
            if (!_initialized) return;

            DriveBody(state.Head);
            DriveHead(state.Head);
            DriveFingers(state.LeftHand,  isLeft: true);
            DriveFingers(state.RightHand, isLeft: false);
            DriveArm(in _leftArm,  state.LeftHand.Wrist,  _config.LeftHand);
            DriveArm(in _rightArm, state.RightHand.Wrist, _config.RightHand);
        }

        /// <summary>
        /// Applies head/body and a single hand's fingers and arm.
        /// Use from NetworkHand so two NetworkHand instances (left/right) do not
        /// overwrite each other's bone results.
        /// </summary>
        public void ApplyHand(HandState hand, bool isLeft, TransformState head)
        {
            if (!_initialized) return;

            if (Time.frameCount != _lastBodyDriveFrame)
            {
                DriveBody(head);
                DriveHead(head);
                _lastBodyDriveFrame = Time.frameCount;
            }

            DriveFingers(hand, isLeft);

            if (isLeft)
                DriveArm(in _leftArm, hand.Wrist, _config.LeftHand);
            else
                DriveArm(in _rightArm, hand.Wrist, _config.RightHand);
        }

        // ------------------------------------------------------------------ //
        //  Body + Head
        // ------------------------------------------------------------------ //

        private void DriveBody(TransformState head)
        {
            Vector3 rootTarget = new Vector3(head.Position.x, _groundY, head.Position.z);
            _bones.Root.position = rootTarget;

            float headYaw = head.Rotation.eulerAngles.y;
            Quaternion targetYaw = Quaternion.Euler(0f, headYaw, 0f);
            _bones.Root.rotation = Quaternion.Slerp(_bones.Root.rotation, targetYaw, bodyYawSmoothing);
        }

        private void DriveHead(TransformState head)
        {
            Quaternion offset = Quaternion.Euler(_config.Head.rotation);
            _bones.Head.rotation = head.Rotation * offset;
        }

        // ------------------------------------------------------------------ //
        //  Fingers
        // ------------------------------------------------------------------ //

        private void DriveFingers(HandState hand, bool isLeft)
        {
            int side = isLeft ? 0 : 1;
            Application.Scripts.Avatar.Utils.HandOffsets offsets = isLeft ? _config.LeftHand : _config.RightHand;

            DriveOneFinger(hand.Thumb,  side, FingerIndex.Thumb,  offsets.thumb);
            DriveOneFinger(hand.Index,  side, FingerIndex.Index,  offsets.index);
            DriveOneFinger(hand.Middle, side, FingerIndex.Middle, offsets.middle);
            DriveOneFinger(hand.Ring,   side, FingerIndex.Ring,   offsets.ring);
            DriveOneFinger(hand.Pinky,  side, FingerIndex.Pinky,  offsets.pinky);
        }

        private void DriveOneFinger(FingerState finger, int side, int fingerIdx, Application.Scripts.Avatar.Utils.FingerOffsets offsets)
        {
            Quaternion axisOffset = offsets.OffsetAxis;

            DriveJoint(_bones.FingerBones[side, fingerIdx, JointIndex.Metacarpal],
                       finger.Metacarpal.Rotation,   offsets.metacarpal,   axisOffset);
            DriveJoint(_bones.FingerBones[side, fingerIdx, JointIndex.Proximal],
                       finger.Proximal.Rotation,     offsets.proximal,     axisOffset);
            DriveJoint(_bones.FingerBones[side, fingerIdx, JointIndex.Intermediate],
                       finger.Intermediate.Rotation, offsets.intermediate, axisOffset);
        }

        private static void DriveJoint(Transform bone, Quaternion openXRWorldRot,
                                       Application.Scripts.Avatar.Utils.TrackingOffsets offset, Quaternion fingerAxisOffset)
        {
            if (bone == null) return;
            if (bone.parent == null) return;

            Quaternion boneOffset = Quaternion.Euler(offset.rotation) * fingerAxisOffset;
            bone.localRotation = Quaternion.Inverse(bone.parent.rotation)
                                 * openXRWorldRot
                                 * boneOffset;
        }

        // ------------------------------------------------------------------ //
        //  Arms
        // ------------------------------------------------------------------ //

        private void DriveArm(in ArmBoneData arm, TransformState wrist, Application.Scripts.Avatar.Utils.HandOffsets handOffsets)
        {
            Quaternion wristOffset = Quaternion.Euler(handOffsets.wrist.rotation);
            Vector3    targetPos   = wrist.Position;
            Quaternion targetRot   = wrist.Rotation * wristOffset;

            ArmSolveResult result = ArmIKSolver.Solve(
                in arm, targetPos, targetRot, _config.ForearmTwistWeight);

            arm.UpperArm.rotation          = result.UpperArmRotation;
            arm.Forearm.rotation           = result.ForearmRotation;
            arm.ForearmTwist.localRotation = result.ForearmTwistLocalRot;
            arm.Hand.rotation              = result.HandRotation;
        }
    }
}
