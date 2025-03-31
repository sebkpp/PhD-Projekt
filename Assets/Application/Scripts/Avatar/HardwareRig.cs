using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using Application.Scripts.Utils.Extensions;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class HardwareRig : MonoBehaviour
    {
        public HardwareHand leftHand;
        public HardwareHand rightHand;
        public HardwareHeadset headset;
        
        private XRInputState _rigState;
        private Vector3 _playAreaOffsetPosition;
        
        public void SetXRRigOffset(Vector3 offset)
        {
            _playAreaOffsetPosition = offset;
        }
        
        public virtual XRInputState RigState
        {
            get
            {
                _rigState.PlayArea = new TransformState()
                {
                    Position = transform.position - _playAreaOffsetPosition, 
                    Rotation = transform.rotation
                };
                
                _rigState.Head = headset.transform.GetTransformState();

                // HandState hand = _rigState.LeftHand;
                // hand.Wrist = leftHand.HandTrackingData.GetWristTransform(_avatarConfig.LeftHand.wrist);
                // hand = leftHand.HandTrackingData.GetHandPose(_avatarConfig.LeftHand);
                _rigState.LeftHandWrist = leftHand.transform.GetTransformState();
                _rigState.LeftHand = leftHand.HandTrackingData.GetHandPose();

                // HandState state = _rigState.RightHand;
                // state.Wrist = rightHand.HandTrackingData.GetWristTransform(_avatarConfig.RightHand.wrist);
                _rigState.RightHandWrist = rightHand.transform.GetTransformState();
                _rigState.RightHand = rightHand.HandTrackingData.GetHandPose();;
                
                //_rigState.leftHandCommand = leftHand.handCommand;
                //_rigState.rightHandCommand = rightHand.handCommand;
                return _rigState;
            }
        }

        
    }
}
