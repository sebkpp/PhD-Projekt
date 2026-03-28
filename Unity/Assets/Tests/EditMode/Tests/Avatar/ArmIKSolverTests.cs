using NUnit.Framework;
using UnityEngine;
using Application.Scripts.Avatar.Driver;

namespace Avatar.Tests.EditMode
{
    public class ArmIKSolverTests
    {
        [Test]
        public void ExtractTwistAround_PureYAxisRotation_ReturnsSameRotation()
        {
            Quaternion rotation = Quaternion.AngleAxis(90f, Vector3.up);
            Quaternion twist    = ArmIKSolver.ExtractTwistAround(rotation, Vector3.up);

            Assert.That(Quaternion.Angle(twist, rotation), Is.LessThan(0.01f),
                "A rotation purely around Y should extract as 100% twist around Y.");
        }

        [Test]
        public void ExtractTwistAround_PureXAxisRotation_ReturnsIdentityTwistAroundY()
        {
            Quaternion rotation = Quaternion.AngleAxis(90f, Vector3.right);
            Quaternion twist    = ArmIKSolver.ExtractTwistAround(rotation, Vector3.up);

            Assert.That(Quaternion.Angle(twist, Quaternion.identity), Is.LessThan(0.01f),
                "A rotation purely around X has zero twist around Y.");
        }

        [Test]
        public void SolveElbow_FullyExtended_ElbowOnStraightLine()
        {
            Vector3 shoulder = Vector3.zero;
            Vector3 wrist    = new Vector3(0f, 0f, 0.549f); // just under 0.3 + 0.25
            Vector3 hint     = new Vector3(0f, -1f, 0.274f); // below midpoint
            float upper      = 0.3f;
            float fore       = 0.25f;

            Vector3 elbow = ArmIKSolver.SolveElbow(shoulder, wrist, hint, upper, fore);

            // Elbow must be within upper arm length of shoulder.
            Assert.That(Vector3.Distance(shoulder, elbow), Is.EqualTo(upper).Within(0.001f));
            // Elbow must be within forearm length of wrist.
            Assert.That(Vector3.Distance(elbow, wrist), Is.EqualTo(fore).Within(0.001f));
        }

        [Test]
        public void SolveElbow_TargetBeyondReach_ClampedInSolve()
        {
            // SolveElbow itself does NOT clamp — clamping is in Solve().
            // Verify SolveElbow still returns valid positions when d is at max.
            Vector3 shoulder = Vector3.zero;
            float upper      = 0.3f;
            float fore       = 0.25f;
            // Set wrist exactly at max reach - epsilon:
            Vector3 wrist    = new Vector3(0f, 0f, upper + fore - 0.001f);
            Vector3 hint     = new Vector3(0f, -1f, wrist.z * 0.5f);

            Vector3 elbow = ArmIKSolver.SolveElbow(shoulder, wrist, hint, upper, fore);

            Assert.That(float.IsNaN(elbow.x), Is.False, "Elbow X must not be NaN at max reach.");
            Assert.That(float.IsNaN(elbow.y), Is.False, "Elbow Y must not be NaN at max reach.");
            Assert.That(float.IsNaN(elbow.z), Is.False, "Elbow Z must not be NaN at max reach.");
        }

        [Test]
        public void ComputeElbowHint_PalmFacingDown_ElbowHintBehindMidpoint()
        {
            // Euler(-90,0,0) tilts the hand's "up" axis toward +Z (world forward).
            // palmNormal = wristRot * up = (0,0,1).
            // Cross(shoulderToWrist=(1,0,0), palmNormal=(0,0,1)).y = -1  → elbow points down.
            Quaternion wristRot = Quaternion.Euler(-90f, 0f, 0f);
            Vector3 shoulder    = Vector3.zero;
            Vector3 wrist       = new Vector3(0.5f, 0f, 0f); // arm pointing right

            Vector3 hint = ArmIKSolver.ComputeElbowHint(shoulder, wrist, wristRot);

            Vector3 midpoint = (shoulder + wrist) * 0.5f;
            Assert.That(hint.y, Is.LessThan(midpoint.y),
                "Elbow hint should be below midpoint when palm faces down.");
        }
    }
}
