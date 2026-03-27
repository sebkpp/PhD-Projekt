using Fusion;

namespace Application.Scripts.Network.Input.States
{
    public struct XRInputNetworked : INetworkStruct
    {
        // Player Area, e.g., for teleportation
        public TransformStateNetworked PlayArea;

        // Head
        public TransformStateNetworked Head;

        // Left Hand
        public HandStateNetworked LeftHand;

        // Right Hand
        public HandStateNetworked RightHand;
    }
}