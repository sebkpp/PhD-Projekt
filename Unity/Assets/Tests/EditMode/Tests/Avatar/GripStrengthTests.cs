using NUnit.Framework;
using UnityEngine;
using UnityEngine.XR.Hands;
using Application.Scripts.Avatar.Data;
using Application.Scripts.Avatar.Grab;

namespace Avatar.Tests.EditMode
{
    public class GripStrengthTests
    {
        // Helper: create a HandPoseData with a single finger's proximal and distal joints set
        private static HandPoseData MakeFingerPose(
            XRHandJointID proximalId, XRHandJointID distalId,
            Quaternion proximalRot, Quaternion distalRot)
        {
            var pose = new HandPoseData();
            pose.Joints[proximalId.ToIndex()] = new HandJointPose
                { Rotation = proximalRot, IsValid = true };
            pose.Joints[distalId.ToIndex()] = new HandJointPose
                { Rotation = distalRot, IsValid = true };
            return pose;
        }

        [Test]
        public void ComputeFingerCurl_StraightFinger_ReturnsZero()
        {
            // Both joints pointing the same direction -> 0 degrees angle -> curl = 0
            var pose = MakeFingerPose(
                XRHandJointID.IndexProximal, XRHandJointID.IndexDistal,
                Quaternion.identity, Quaternion.identity);

            float curl = GripStrengthCalculator.ComputeFingerCurl(
                pose,
                XRHandJointID.IndexProximal,
                XRHandJointID.IndexIntermediate,
                XRHandJointID.IndexDistal);

            Assert.That(curl, Is.EqualTo(0f).Within(0.01f));
        }

        [Test]
        public void ComputeFingerCurl_FullyCurledFinger_ReturnsOne()
        {
            // Proximal points forward, distal rotated 90 degrees back -> max curl
            var proxRot = Quaternion.identity;
            var distalRot = Quaternion.AngleAxis(90f, Vector3.right); // 90 degree angle between them
            var pose = MakeFingerPose(
                XRHandJointID.IndexProximal, XRHandJointID.IndexDistal,
                proxRot, distalRot);

            float curl = GripStrengthCalculator.ComputeFingerCurl(
                pose,
                XRHandJointID.IndexProximal,
                XRHandJointID.IndexIntermediate,
                XRHandJointID.IndexDistal);

            Assert.That(curl, Is.GreaterThanOrEqualTo(0.95f));
        }

        [Test]
        public void ComputeFingerCurl_InvalidJoint_ReturnsZero()
        {
            // Empty pose -> all IsValid = false -> should return 0
            var pose = new HandPoseData();
            float curl = GripStrengthCalculator.ComputeFingerCurl(
                pose,
                XRHandJointID.IndexProximal,
                XRHandJointID.IndexIntermediate,
                XRHandJointID.IndexDistal);

            Assert.That(curl, Is.EqualTo(0f));
        }

        [Test]
        public void ComputeGripStrength_AllFingersCurled_ReturnsOne()
        {
            var pose = new HandPoseData();
            Quaternion curled = Quaternion.AngleAxis(90f, Vector3.right);
            // Set proximal and distal for all four fingers
            foreach (var (p, i, d) in new[]
            {
                (XRHandJointID.IndexProximal,  XRHandJointID.IndexIntermediate,  XRHandJointID.IndexDistal),
                (XRHandJointID.MiddleProximal, XRHandJointID.MiddleIntermediate, XRHandJointID.MiddleDistal),
                (XRHandJointID.RingProximal,   XRHandJointID.RingIntermediate,   XRHandJointID.RingDistal),
                (XRHandJointID.LittleProximal, XRHandJointID.LittleIntermediate, XRHandJointID.LittleDistal),
            })
            {
                pose.Joints[p.ToIndex()] = new HandJointPose { Rotation = Quaternion.identity, IsValid = true };
                pose.Joints[d.ToIndex()] = new HandJointPose { Rotation = curled, IsValid = true };
            }

            float grip = GripStrengthCalculator.ComputeGripStrength(pose);
            Assert.That(grip, Is.GreaterThanOrEqualTo(0.9f));
        }

        [Test]
        public void ComputeGripStrength_AllFingersOpen_ReturnsZero()
        {
            var pose = new HandPoseData();
            foreach (var id in new[]
            {
                XRHandJointID.IndexProximal, XRHandJointID.IndexDistal,
                XRHandJointID.MiddleProximal, XRHandJointID.MiddleDistal,
                XRHandJointID.RingProximal,   XRHandJointID.RingDistal,
                XRHandJointID.LittleProximal, XRHandJointID.LittleDistal,
            })
            {
                pose.Joints[id.ToIndex()] = new HandJointPose { Rotation = Quaternion.identity, IsValid = true };
            }

            float grip = GripStrengthCalculator.ComputeGripStrength(pose);
            Assert.That(grip, Is.EqualTo(0f).Within(0.05f));
        }
    }
}
