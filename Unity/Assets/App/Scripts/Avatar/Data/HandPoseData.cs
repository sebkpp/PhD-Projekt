using UnityEngine;
using UnityEngine.XR.Hands;

namespace Application.Scripts.Avatar.Data
{
    /// <summary>
    /// One joint from OpenXR: world-space position, rotation, and validity flag.
    /// </summary>
    public struct HandJointPose
    {
        public Vector3 Position;
        public Quaternion Rotation;
        public bool IsValid;
    }

    /// <summary>
    /// Full hand pose from OpenXR XRHandSubsystem — 26 joints indexed by XRHandJointID.
    /// This is a class (not struct) so it can be updated in-place each frame without allocation.
    /// </summary>
    public class HandPoseData
    {
        /// <summary>True when the XR subsystem is actively tracking this hand.</summary>
        public bool IsTracked;

        /// <summary>
        /// All 26 joint poses. Index using <c>XRHandJointID.ToIndex()</c>.
        /// Array length is <c>XRHandJointID.EndMarker.ToIndex()</c>.
        /// </summary>
        public readonly HandJointPose[] Joints;

        public HandPoseData()
        {
            Joints = new HandJointPose[XRHandJointID.EndMarker.ToIndex()];
        }

        /// <summary>Returns the pose for a specific joint, or an invalid pose if out of range.</summary>
        public HandJointPose GetJoint(XRHandJointID jointId)
        {
            int index = jointId.ToIndex();
            if (index < 0 || index >= Joints.Length) return default;
            return Joints[index];
        }

        /// <summary>
        /// Converts this HandPoseData into a HandState suitable for networking.
        /// OpenXR joints map to Rocketbox bones as follows:
        /// - OpenXR Metacarpal → FingerState.Metacarpal (drives Bip01 Finger0/1/2/3/4)
        /// - OpenXR Proximal   → FingerState.Proximal   (drives Bip01 Finger01/11/21/31/41)
        /// - OpenXR Intermediate → FingerState.Intermediate
        /// - OpenXR Distal (ignored by avatar driver, kept for completeness)
        /// </summary>
        public Application.Scripts.Interaction.States.HandState ToHandState()
        {
            return new Application.Scripts.Interaction.States.HandState
            {
                Wrist  = JointToTransformState(XRHandJointID.Wrist),
                Thumb  = FingerToState(XRHandJointID.ThumbMetacarpal,   XRHandJointID.ThumbProximal,   XRHandJointID.ThumbDistal,        XRHandJointID.ThumbTip),
                Index  = FingerToState(XRHandJointID.IndexMetacarpal,   XRHandJointID.IndexProximal,   XRHandJointID.IndexIntermediate,  XRHandJointID.IndexDistal),
                Middle = FingerToState(XRHandJointID.MiddleMetacarpal,  XRHandJointID.MiddleProximal,  XRHandJointID.MiddleIntermediate, XRHandJointID.MiddleDistal),
                Ring   = FingerToState(XRHandJointID.RingMetacarpal,    XRHandJointID.RingProximal,    XRHandJointID.RingIntermediate,   XRHandJointID.RingDistal),
                Pinky  = FingerToState(XRHandJointID.LittleMetacarpal,  XRHandJointID.LittleProximal,  XRHandJointID.LittleIntermediate, XRHandJointID.LittleDistal),
            };
        }

        private Application.Scripts.Interaction.States.FingerState FingerToState(
            XRHandJointID metacarpal, XRHandJointID proximal,
            XRHandJointID intermediate, XRHandJointID distal)
        {
            return new Application.Scripts.Interaction.States.FingerState
            {
                Metacarpal   = JointToTransformState(metacarpal),
                Proximal     = JointToTransformState(proximal),
                Intermediate = JointToTransformState(intermediate),
                Distal       = JointToTransformState(distal),
            };
        }

        private Application.Scripts.Interaction.States.TransformState JointToTransformState(XRHandJointID id)
        {
            HandJointPose j = GetJoint(id);
            return new Application.Scripts.Interaction.States.TransformState
            {
                Position = j.Position,
                Rotation = j.IsValid ? j.Rotation : Quaternion.identity,
            };
        }
    }
}
