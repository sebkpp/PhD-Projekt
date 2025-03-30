using Application.Scripts.Interaction;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public struct FingerState
    {
        public TransformState Proximal { get; set; }
        public TransformState Intermediate { get; set; }
        public TransformState Distal { get; set; }
    }
    
    public struct HandState
    {
        public TransformState Wrist { get; set; }
        
        public FingerState Thumb { get; set; }
        public FingerState Index { get; set; }
        public FingerState Middle { get; set; }
        public FingerState Ring { get; set; }
        public FingerState Pinky { get; set; }
    }
}