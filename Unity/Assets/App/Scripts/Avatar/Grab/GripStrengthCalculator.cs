using Application.Scripts.Avatar.Data;
using Application.Scripts.Avatar.Hardware;
using UnityEngine;
using UnityEngine.XR.Hands;

namespace Application.Scripts.Avatar.Grab
{
    /// <summary>
    /// Reads XR Hand joint data from HardwareHand and computes per-hand grip strength (0-1)
    /// and grip type classification each frame.
    /// </summary>
    public class GripStrengthCalculator : MonoBehaviour
    {
        /// <summary>Raw grip strength based on finger curl, ignoring contact. Range 0-1.</summary>
        public float GripStrength { get; private set; }

        /// <summary>Classified grip type based on finger configuration this frame.</summary>
        public GripType CurrentGripType { get; private set; }

        private HardwareHand _hardwareHand;

        private void Awake()
        {
            _hardwareHand = GetComponent<HardwareHand>();
            if (_hardwareHand == null)
                Debug.LogError("[GripStrengthCalculator] Requires a HardwareHand on the same GameObject.");
        }

        private void Update()
        {
            if (_hardwareHand == null || !_hardwareHand.CurrentPose.IsTracked)
            {
                GripStrength = 0f;
                CurrentGripType = GripType.Undefined;
                return;
            }

            HandPoseData pose = _hardwareHand.CurrentPose;
            GripStrength = ComputeGripStrength(pose);
            CurrentGripType = ClassifyGripType(pose);
        }

        /// <summary>
        /// Computes curl for a single finger from the angle between proximal and distal joint directions.
        /// Returns 0 if joints are invalid. Range 0 (straight) to 1 (fully curled at 90 degrees).
        /// Public and static for unit testing.
        /// </summary>
        public static float ComputeFingerCurl(
            HandPoseData pose,
            XRHandJointID proximalId,
            XRHandJointID intermediateId,
            XRHandJointID distalId)
        {
            HandJointPose proximal = pose.GetJoint(proximalId);
            HandJointPose distal   = pose.GetJoint(distalId);
            if (!proximal.IsValid || !distal.IsValid) return 0f;

            Vector3 proximalDir = proximal.Rotation * Vector3.forward;
            Vector3 distalDir   = distal.Rotation   * Vector3.forward;
            return Mathf.Clamp01(Vector3.Angle(proximalDir, distalDir) / 90f);
        }

        /// <summary>
        /// Weighted average of the four non-thumb finger curls.
        /// Middle/ring/little weighted heavier (power grip), index moderate.
        /// Public and static for unit testing.
        /// </summary>
        public static float ComputeGripStrength(HandPoseData pose)
        {
            float index  = ComputeFingerCurl(pose, XRHandJointID.IndexProximal,  XRHandJointID.IndexIntermediate,  XRHandJointID.IndexDistal);
            float middle = ComputeFingerCurl(pose, XRHandJointID.MiddleProximal, XRHandJointID.MiddleIntermediate, XRHandJointID.MiddleDistal);
            float ring   = ComputeFingerCurl(pose, XRHandJointID.RingProximal,   XRHandJointID.RingIntermediate,   XRHandJointID.RingDistal);
            float little = ComputeFingerCurl(pose, XRHandJointID.LittleProximal, XRHandJointID.LittleIntermediate, XRHandJointID.LittleDistal);
            return index * 0.2f + middle * 0.3f + ring * 0.3f + little * 0.2f;
        }

        private static GripType ClassifyGripType(HandPoseData pose)
        {
            float indexCurl  = ComputeFingerCurl(pose, XRHandJointID.IndexProximal,  XRHandJointID.IndexIntermediate,  XRHandJointID.IndexDistal);
            float middleCurl = ComputeFingerCurl(pose, XRHandJointID.MiddleProximal, XRHandJointID.MiddleIntermediate, XRHandJointID.MiddleDistal);

            HandJointPose thumbTip = pose.GetJoint(XRHandJointID.ThumbTip);
            HandJointPose indexTip = pose.GetJoint(XRHandJointID.IndexTip);

            float pinchDistance = (thumbTip.IsValid && indexTip.IsValid)
                ? Vector3.Distance(thumbTip.Position, indexTip.Position)
                : 1f;

            if (pinchDistance < 0.025f && middleCurl < 0.5f)
                return GripType.PrecisionPinch;

            if (pinchDistance < 0.045f && indexCurl < 0.4f)
                return GripType.LateralPinch;

            if (indexCurl > 0.6f && middleCurl > 0.6f)
                return GripType.PowerGrip;

            return GripType.Undefined;
        }
    }
}
