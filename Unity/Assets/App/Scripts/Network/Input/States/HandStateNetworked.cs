using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
using Fusion;

namespace Application.Scripts.Network.Input.States
{
    /// <summary>
    /// Represents the network-synchronized transform states of a single finger,
    /// including its metacarpal, proximal, intermediate, and distal joints.
    /// </summary>
    public struct FingerStateNetworked : INetworkStruct
    {
        /// <summary>
        /// The transform state of the metacarpal joint of the finger.
        /// </summary>
        public TransformStateNetworked Metacarpal;

        /// <summary>
        /// The transform state of the proximal (base) joint of the finger.
        /// </summary>
        public TransformStateNetworked Proximal;

        /// <summary>
        /// The transform state of the intermediate (middle) joint of the finger.
        /// </summary>
        public TransformStateNetworked Intermediate;

        /// <summary>
        /// The transform state of the distal (tip) joint of the finger.
        /// </summary>
        public TransformStateNetworked Distal;

        /// <summary>
        /// Converts the networked finger state into a local <see cref="FingerState"/> representation.
        /// </summary>
        /// <returns>A new <see cref="FingerState"/> with equivalent transform data.</returns>
        public FingerState ToFingerState()
        {
            return new FingerState
            {
                Metacarpal   = new TransformState { Position = Metacarpal.Position,   Rotation = Metacarpal.Rotation },
                Proximal     = new TransformState { Position = Proximal.Position,     Rotation = Proximal.Rotation },
                Intermediate = new TransformState { Position = Intermediate.Position, Rotation = Intermediate.Rotation },
                Distal       = new TransformState { Position = Distal.Position,       Rotation = Distal.Rotation },
            };
        }

        /// <summary>
        /// Creates a <see cref="FingerStateNetworked"/> from a local <see cref="FingerState"/>.
        /// </summary>
        /// <param name="fingerState">The local finger state to convert.</param>
        /// <returns>A new <see cref="FingerStateNetworked"/> with corresponding networked data.</returns>
        public static FingerStateNetworked FromFingerState(FingerState fingerState)
        {
            return new FingerStateNetworked
            {
                Metacarpal   = new TransformStateNetworked { Position = fingerState.Metacarpal.Position,   Rotation = fingerState.Metacarpal.Rotation },
                Proximal     = new TransformStateNetworked { Position = fingerState.Proximal.Position,     Rotation = fingerState.Proximal.Rotation },
                Intermediate = new TransformStateNetworked { Position = fingerState.Intermediate.Position, Rotation = fingerState.Intermediate.Rotation },
                Distal       = new TransformStateNetworked { Position = fingerState.Distal.Position,       Rotation = fingerState.Distal.Rotation },
            };
        }
    }
    
    /// <summary>
    /// Represents the full network-synchronized hand pose,
    /// including wrist and all five fingers (thumb, index, middle, ring, pinky).
    /// </summary>
    public struct HandStateNetworked : INetworkStruct
    {
        /// <summary>
        /// The transform state of the wrist.
        /// </summary>
        public TransformStateNetworked Wrist;
        
        /// <summary>
        /// The networked transform states for the thumb finger.
        /// </summary>
        public FingerStateNetworked Thumb;
        
        /// <summary>
        /// The networked transform states for the index finger.
        /// </summary>
        public FingerStateNetworked Index;
        
        /// <summary>
        /// The networked transform states for the middle finger.
        /// </summary>
        public FingerStateNetworked Middle;
        
        /// <summary>
        /// The networked transform states for the ring finger.
        /// </summary>
        public FingerStateNetworked Ring;
        
        /// <summary>
        /// The networked transform states for the pinky finger.
        /// </summary>
        public FingerStateNetworked Pinky;
        
        
        /// <summary>
        /// Implicitly converts a <see cref="HandStateNetworked"/> to a local <see cref="HandState"/>.
        /// </summary>
        /// <param name="networked">The networked hand state to convert.</param>
        public static implicit operator HandState(HandStateNetworked networked)
        {
            return new HandState
            {
                Wrist = new TransformState{ Position = networked.Wrist.Position, Rotation = networked.Wrist.Rotation},
                
                Thumb = networked.Thumb.ToFingerState(),
                Index = networked.Index.ToFingerState(),
                Middle = networked.Middle.ToFingerState(),
                Ring = networked.Ring.ToFingerState(),
                Pinky = networked.Pinky.ToFingerState()
            };
        }
        
        /// <summary>
        /// Explicitly converts a local <see cref="HandState"/> to a <see cref="HandStateNetworked"/>.
        /// </summary>
        /// <param name="hand">The local hand state to convert.</param>
        public static explicit operator HandStateNetworked(HandState hand)
        {
            return new HandStateNetworked
            {
                Wrist = new TransformStateNetworked{ Position = hand.Wrist.Position, Rotation = hand.Wrist.Rotation},
                
                Thumb = FingerStateNetworked.FromFingerState(hand.Thumb),
                Index = FingerStateNetworked.FromFingerState(hand.Index),
                Middle = FingerStateNetworked.FromFingerState(hand.Middle),
                Ring = FingerStateNetworked.FromFingerState(hand.Ring),
                Pinky = FingerStateNetworked.FromFingerState(hand.Pinky)
            };
        }
    }
}