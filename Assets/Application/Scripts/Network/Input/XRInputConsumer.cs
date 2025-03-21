using Application.Scripts.Avatar_rigging;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public class XRInputConsumer : NetworkBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform avatarPosition;
        [SerializeField] private Transform avatarHead;
        [SerializeField] private HandRig avatarLeftHand;
        [SerializeField] private HandRig avatarRightHand;
        
        public override void FixedUpdateNetwork()
        {
            if (GetInput<XRInputState>(out var input) == false) return;
            
            //avatarPosition.SetPositionAndRotation(input.PlayAreaPosition, input.PlayAreaRotation);
            avatarHead.SetPositionAndRotation(input.HeadsetPosition, input.HeadsetRotation);
            ApplyHandState(avatarLeftHand, input.LeftHand);
            ApplyHandState(avatarRightHand, input.RightHand);
        }

        private void ApplyHandState(HandRig hand, HandState handState)
        {
            hand.wrist.SetPositionAndRotation(handState.WristPosition, handState.WristRotation);
            ApplyFingerState(hand.thumb, handState.Thumb);
            ApplyFingerState(hand.index, handState.Index);
            ApplyFingerState(hand.middle, handState.Middle);
            ApplyFingerState(hand.ring, handState.Ring);
            ApplyFingerState(hand.pinky, handState.Pinky);
        }

        private void ApplyFingerState(FingerRig finger, FingerState state)
        {
            finger.proximal.SetPositionAndRotation(state.Proximal.Position, state.Proximal.Rotation);
            finger.intermediate.SetPositionAndRotation(state.Intermediate.Position, state.Intermediate.Rotation);
            finger.distal.SetPositionAndRotation(state.Distal.Position, state.Distal.Rotation);
        }
    }
}