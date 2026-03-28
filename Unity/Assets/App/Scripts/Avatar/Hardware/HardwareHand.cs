using System.Collections.Generic;
using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Data;
using UnityEngine;
using UnityEngine.XR.Hands;

namespace Application.Scripts.Avatar.Hardware
{
    /// <summary>
    /// Reads optical hand tracking data from the OpenXR XRHandSubsystem each frame.
    /// Exposes the full 26-joint HandPoseData for use by HardwareRig and AvatarDriver.
    /// </summary>
    public class HardwareHand : MonoBehaviour
    {
        [SerializeField] private Handedness handedness;
        [SerializeField] private RigPart side;

        /// <summary>Current full hand pose, updated every frame when subsystem is active.</summary>
        public HandPoseData CurrentPose { get; } = new HandPoseData();

        /// <summary>Whether this hand is currently performing a grab gesture.</summary>
        public bool IsGrabbing { get; set; }

        public RigPart Side => side;

        private XRHandSubsystem _subsystem;
        private static readonly List<XRHandSubsystem> s_Subsystems = new List<XRHandSubsystem>();

        private void Update()
        {
            EnsureSubsystem();
            if (_subsystem == null)
            {
                CurrentPose.IsTracked = false;
                return;
            }

            XRHand hand = handedness == Handedness.Left ? _subsystem.leftHand : _subsystem.rightHand;
            CurrentPose.IsTracked = hand.isTracked;
            if (!hand.isTracked) return;

            int end = XRHandJointID.EndMarker.ToIndex();
            for (int i = XRHandJointID.BeginMarker.ToIndex(); i < end; i++)
            {
                XRHandJointID jointId = XRHandJointIDUtility.FromIndex(i);
                XRHandJoint   joint   = hand.GetJoint(jointId);

                if (joint.TryGetPose(out Pose pose))
                {
                    CurrentPose.Joints[i] = new HandJointPose
                    {
                        Position = pose.position,
                        Rotation = pose.rotation,
                        IsValid  = true,
                    };
                }
                else
                {
                    CurrentPose.Joints[i] = default;
                }
            }
        }

        private void EnsureSubsystem()
        {
            if (_subsystem != null && _subsystem.running) return;

            _subsystem = null;
            SubsystemManager.GetSubsystems(s_Subsystems);
            foreach (var sub in s_Subsystems)
            {
                if (sub.running)
                {
                    _subsystem = sub;
                    break;
                }
            }
        }
    }
}
