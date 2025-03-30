using Application.Scripts.Interaction;
using Fusion;

namespace Application.Scripts.Network.Input
{
    public struct FingerStateNetworked : INetworkStruct
    {
        public TransformStateNetworked Proximal;
        public TransformStateNetworked Intermediate;
        public TransformStateNetworked Distal;
        
        public FingerState ToFingerState()
        {
            return new FingerState
            {
                Proximal = new TransformState { Position = Proximal.Position, Rotation = Proximal.Rotation },
                Intermediate = new TransformState { Position = Intermediate.Position, Rotation = Intermediate.Rotation },
                Distal = new TransformState { Position = Distal.Position, Rotation = Distal.Rotation }
            };
        }

        public static FingerStateNetworked FromFingerState(FingerState fingerState)
        {
            return new FingerStateNetworked
            {
                Proximal = new TransformStateNetworked { Position = fingerState.Proximal.Position, Rotation = fingerState.Proximal.Rotation },
                Intermediate = new TransformStateNetworked { Position = fingerState.Intermediate.Position, Rotation = fingerState.Intermediate.Rotation },
                Distal = new TransformStateNetworked { Position = fingerState.Distal.Position, Rotation = fingerState.Distal.Rotation }
            };
        }
    }
    
    public struct HandStateNetworked : INetworkStruct
    {
        public FingerStateNetworked Thumb;
        public FingerStateNetworked Index;
        public FingerStateNetworked Middle;
        public FingerStateNetworked Ring;
        public FingerStateNetworked Pinky;
        
        
        /// <summary>
        /// implicit converts to HandState
        /// </summary>
        public static implicit operator HandState(HandStateNetworked networked)
        {
            return new HandState
            {
                Thumb = networked.Thumb.ToFingerState(),
                Index = networked.Index.ToFingerState(),
                Middle = networked.Middle.ToFingerState(),
                Ring = networked.Ring.ToFingerState(),
                Pinky = networked.Pinky.ToFingerState()
            };
        }
        
        public static explicit operator HandStateNetworked(HandState hand)
        {
            return new HandStateNetworked
            {
                Thumb = FingerStateNetworked.FromFingerState(hand.Thumb),
                Index = FingerStateNetworked.FromFingerState(hand.Index),
                Middle = FingerStateNetworked.FromFingerState(hand.Middle),
                Ring = FingerStateNetworked.FromFingerState(hand.Ring),
                Pinky = FingerStateNetworked.FromFingerState(hand.Pinky)
            };
        }
    }
}