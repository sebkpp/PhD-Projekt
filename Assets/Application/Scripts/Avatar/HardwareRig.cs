using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
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
                
                _rigState.LeftHand = leftHand.HandTrackingData.GetHandPose();
                _rigState.RightHand = rightHand.HandTrackingData.GetHandPose();;
                
                //_rigState.leftHandCommand = leftHand.handCommand;
                //_rigState.rightHandCommand = rightHand.handCommand;
                return _rigState;
            }
        }

        
    }
}
