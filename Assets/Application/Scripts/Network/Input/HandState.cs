using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public struct PhalanxState : INetworkStruct
    {
        public Vector3 Position { get; set; }
        public Quaternion Rotation { get; set; }
    }
    
    public struct FingerState : INetworkStruct
    {
        public PhalanxState Proximal { get; set; }
        public PhalanxState Intermediate { get; set; }
        public PhalanxState Distal { get; set; }
    }
    
    public struct HandState : INetworkStruct
    {
        public Vector3 WristPosition { get; set; }
        public Quaternion WristRotation { get; set; }
        
        public FingerState Thumb { get; set; }
        public FingerState Index { get; set; }
        public FingerState Middle { get; set; }
        public FingerState Ring { get; set; }
        public FingerState Pinky { get; set; }
    }
}