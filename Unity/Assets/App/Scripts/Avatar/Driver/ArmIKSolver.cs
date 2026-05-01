using UnityEngine;

namespace Application.Scripts.Avatar.Driver
{
    /// <summary>
    /// Stores the bone data for one arm, captured at avatar initialization (T-pose).
    /// All lengths and rest-pose directions are computed once and reused each frame.
    /// </summary>
    public struct ArmBoneData
    {
        public Transform UpperArm;
        public Transform Forearm;
        public Transform ForearmTwist;  // virtual bone inserted at runtime
        public Transform Hand;

        public float UpperArmLength;
        public float ForearmLength;

        // World-space bone directions at T-pose — used to compute rotation deltas.
        public Quaternion RestUpperArmRotation;
        public Quaternion RestForearmRotation;
        public Vector3 RestUpperArmDir;  // shoulder → elbow at T-pose
        public Vector3 RestForearmDir;   // elbow → wrist at T-pose

        /// <summary>
        /// Captures the current world state of the arm as the rest pose.
        /// Call this once after avatar instantiation while it is in T-pose.
        /// </summary>
        public static ArmBoneData Build(Transform upperArm, Transform forearm, Transform forearmTwist, Transform hand)
        {
            return new ArmBoneData
            {
                UpperArm = upperArm,
                Forearm = forearm,
                ForearmTwist = forearmTwist,
                Hand = hand,
                UpperArmLength = Vector3.Distance(upperArm.position, forearm.position),
                ForearmLength = Vector3.Distance(forearm.position, hand.position),
                RestUpperArmRotation = upperArm.rotation,
                RestForearmRotation = forearm.rotation,
                RestUpperArmDir = (forearm.position - upperArm.position).normalized,
                RestForearmDir = (hand.position - forearm.position).normalized,
            };
        }
    }

    /// <summary>
    /// Output of one arm IK solve.  Set these on the bone transforms every LateUpdate.
    /// </summary>
    public struct ArmSolveResult
    {
        public Quaternion UpperArmRotation;      // world rotation for UpperArm
        public Quaternion ForearmRotation;       // world rotation for Forearm (swing only, no twist)
        public Quaternion ForearmTwistLocalRot;  // LOCAL rotation for the virtual ForearmTwist bone
        public Quaternion HandRotation;          // world rotation for Hand (full target rotation)
    }

    /// <summary>
    /// Pure-static analytic 2-bone IK solver for VR avatar arms.
    /// Elbow direction is derived from wrist rotation so it stays anatomically correct
    /// as the hand pronates/supinates.  Forearm twist is distributed via a virtual
    /// intermediate bone (ForearmTwist) that sits between Forearm and Hand.
    /// </summary>
    public static class ArmIKSolver
    {
        private const float k_MinReachEpsilon = 0.001f;

        /// <summary>
        /// Solve the arm IK for one frame.
        /// </summary>
        /// <param name="arm">Rest-pose bone data captured at avatar init.</param>
        /// <param name="targetWristPos">Target wrist world position (from OpenXR).</param>
        /// <param name="targetWristRot">Target wrist world rotation (from OpenXR).</param>
        /// <param name="forearmTwistWeight">Fraction of forearm twist given to ForearmTwist bone [0,1].</param>
        public static ArmSolveResult Solve(
            in ArmBoneData arm,
            Vector3 targetWristPos,
            Quaternion targetWristRot,
            float forearmTwistWeight = 0.5f)
        {
            Vector3 shoulderPos = arm.UpperArm.position;
            float maxReach = arm.UpperArmLength + arm.ForearmLength - k_MinReachEpsilon;

            // Clamp target to reachable range.
            Vector3 shoulderToTarget = targetWristPos - shoulderPos;
            if (shoulderToTarget.magnitude > maxReach)
                targetWristPos = shoulderPos + shoulderToTarget.normalized * maxReach;

            // Compute elbow hint from wrist palm direction.
            Vector3 elbowHintPos = ComputeElbowHint(shoulderPos, targetWristPos, targetWristRot);

            // Solve triangle to find elbow world position.
            Vector3 elbowPos = SolveElbow(
                shoulderPos, targetWristPos, elbowHintPos,
                arm.UpperArmLength, arm.ForearmLength);

            // Derive world rotations using FromToRotation on rest-pose directions.
            Vector3 upperArmDir = (elbowPos - shoulderPos).normalized;
            Vector3 forearmDir  = (targetWristPos - elbowPos).normalized;

            Quaternion upperArmRot = Quaternion.FromToRotation(arm.RestUpperArmDir, upperArmDir)
                                     * arm.RestUpperArmRotation;

            Quaternion forearmRot  = Quaternion.FromToRotation(arm.RestForearmDir, forearmDir)
                                     * arm.RestForearmRotation;

            // Extract twist from target wrist rotation and distribute it.
            Quaternion twist = ExtractTwistAround(targetWristRot, forearmDir);

            // ForearmTwist gets a fraction of the twist as a LOCAL rotation relative to Forearm.
            Quaternion forearmTwistLocalRot = Quaternion.Slerp(Quaternion.identity, twist, forearmTwistWeight);

            return new ArmSolveResult
            {
                UpperArmRotation     = upperArmRot,
                ForearmRotation      = forearmRot,
                ForearmTwistLocalRot = forearmTwistLocalRot,
                HandRotation         = targetWristRot,
            };
        }

        /// <summary>
        /// Computes an elbow hint position that reflects the anatomically correct bend
        /// direction based on the wrist rotation (palm normal).
        /// </summary>
        public static Vector3 ComputeElbowHint(Vector3 shoulderPos, Vector3 wristPos, Quaternion wristRot)
        {
            // The back-of-hand normal tells us which way the elbow should point.
            Vector3 palmNormal      = wristRot * Vector3.up;
            Vector3 shoulderToWrist = (wristPos - shoulderPos).normalized;
            Vector3 cross    = Vector3.Cross(shoulderToWrist, palmNormal);
            Vector3 elbowDir = cross.sqrMagnitude < 0.001f ? -Vector3.forward : cross.normalized;

            Vector3 midpoint = (shoulderPos + wristPos) * 0.5f;
            return midpoint + elbowDir * 0.15f;
        }

        /// <summary>
        /// Given shoulder, target wrist, and a hint for bend direction, returns elbow world position.
        /// Uses the law of cosines for an analytic solution.
        /// </summary>
        public static Vector3 SolveElbow(
            Vector3 shoulder, Vector3 wrist, Vector3 hint,
            float upperArmLen, float forearmLen)
        {
            float d = Mathf.Clamp(
                Vector3.Distance(shoulder, wrist),
                k_MinReachEpsilon,
                upperArmLen + forearmLen - k_MinReachEpsilon);

            // Law of cosines: angle at shoulder.
            float cosA = (upperArmLen * upperArmLen + d * d - forearmLen * forearmLen)
                         / (2f * upperArmLen * d);
            float angleA = Mathf.Acos(Mathf.Clamp(cosA, -1f, 1f));

            Vector3 shoulderToWrist = (wrist - shoulder).normalized;
            Vector3 shoulderToHint  = (hint  - shoulder).normalized;
            Vector3 bendNormal      = Vector3.Cross(shoulderToWrist, shoulderToHint).normalized;

            if (bendNormal.sqrMagnitude < 0.001f)
                bendNormal = Vector3.right; // Fallback if hint is collinear.

            // Rotate the shoulder→wrist direction by angleA around bendNormal.
            Quaternion rot    = Quaternion.AngleAxis(angleA * Mathf.Rad2Deg, bendNormal);
            Vector3 elbowDir  = rot * shoulderToWrist;

            return shoulder + elbowDir * upperArmLen;
        }

        /// <summary>
        /// Decomposes <paramref name="rotation"/> into a twist component around <paramref name="axis"/>
        /// and an implicit swing component.  Returns the twist quaternion.
        /// </summary>
        public static Quaternion ExtractTwistAround(Quaternion rotation, Vector3 axis)
        {
            axis = axis.normalized;
            // Project the quaternion's vector part onto the axis (standard swing-twist decomposition).
            // Do NOT rotate the axis by the rotation first — that gives the wrong projection.
            Vector3 projected = Vector3.Project(new Vector3(rotation.x, rotation.y, rotation.z), axis);
            var twist = new Quaternion(projected.x, projected.y, projected.z, rotation.w);

            float mag = Mathf.Sqrt(twist.x * twist.x + twist.y * twist.y + twist.z * twist.z + twist.w * twist.w);
            if (mag < 0.001f) return Quaternion.identity;

            return new Quaternion(twist.x / mag, twist.y / mag, twist.z / mag, twist.w / mag);
        }
    }
}
