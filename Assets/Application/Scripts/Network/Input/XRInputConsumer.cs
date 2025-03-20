using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public class XRInputConsumer : NetworkBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform avatarPosition;
        [SerializeField] private Transform avatarHead;
        [SerializeField] private Transform avatarLeftHand;
        [SerializeField] private Transform avatarRightHand;
        
        public override void FixedUpdateNetwork()
        {
            if (GetInput<XRInputState>(out var input) == false) return;
            
            avatarPosition.SetPositionAndRotation(input.PlayAreaPosition, input.PlayAreaRotation);
            avatarHead.SetPositionAndRotation(input.HeadsetPosition, input.HeadsetRotation);
            avatarLeftHand.SetPositionAndRotation(input.LeftHandPosition, input.LeftHandRotation);
            avatarRightHand.SetPositionAndRotation(input.RightHandPosition, input.RightHandRotation);
        }
    }
}