using Application.Scripts.Avatar_rigging;
using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using Application.Scripts.Utils.Extensions;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class HardwareRig : MonoBehaviour
    {
        public TrackingData playArea;
        public HardwareHand leftHand;
        public HardwareHand rightHand;
        public HardwareHeadset headset;
        
        private XRInputState _rigState;

        public void SetXRRigOffset(Vector3 offset)
        {
            playArea.offsetPosition = offset;
        }
        
        public virtual XRInputState RigState
        {
            get
            {
                _rigState.PlayArea = new TransformState(){Position = transform.position - playArea.offsetPosition, Rotation = transform.rotation};
                
                _rigState.Head = headset.trackingData.GetState();
                
                _rigState.LeftHand = leftHand.HandTrackingData.GetHandState();
                _rigState.RightHand = rightHand.HandTrackingData.GetHandState();
                
                //_rigState.leftHandCommand = leftHand.handCommand;
                //_rigState.rightHandCommand = rightHand.handCommand;
                return _rigState;
            }
        }

        
    }
}
