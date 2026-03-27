using System;
using UnityEngine;

namespace Application.Scripts.Utils.Test
{
    [ExecuteInEditMode]
    public class Transformation : MonoBehaviour
    {
        [SerializeField] private Transform sourceWrist;
        [SerializeField] private Transform sourceJoint1;
        [SerializeField] private Transform sourceJoint2;

        [SerializeField] private Transform targetWrist;
        [SerializeField] private Vector3 targetWristOffset;
        [SerializeField] private Vector3 targetWristOffsetPosition;

        [SerializeField] private Transform targetJoint1;
        [SerializeField] private Transform targetJoint2;
        [SerializeField] private Vector3 targetJointOffset;
        [SerializeField] private Vector3 forwardAxis = new Vector3(0, 0, 1);
        [SerializeField] private Vector3 upwardsAxis = new Vector3(0, 1, 0);
        private Quaternion _sourceToTargetBasis;

        private void Update()
        {

            targetWrist.position = sourceWrist.position + targetWristOffsetPosition;
            Vector3 sourceGlobalPosition = sourceJoint1.position ;

            Vector3 localTargetPosition = targetJoint1.parent.InverseTransformPoint(sourceGlobalPosition);
            targetJoint1.position = targetJoint1.parent.TransformPoint(localTargetPosition);
            targetWrist.rotation = sourceWrist.rotation * Quaternion.Euler(targetWristOffset);

            _sourceToTargetBasis = Quaternion.Inverse(Quaternion.LookRotation(
                forwardAxis,
                upwardsAxis
            ));


            targetJoint1.rotation = sourceJoint1.rotation * Quaternion.Euler(targetJointOffset) * _sourceToTargetBasis;

            Debug.Log($"{sourceJoint1.rotation.eulerAngles} * {targetJointOffset} * {_sourceToTargetBasis.eulerAngles} = {targetJoint1.rotation.eulerAngles}");

            //targetJoint2.localRotation = sourceToTargetRotation * Quaternion.Euler(targetJointOffset) * localSourceJoint2;
        }
    }
}
