namespace Application.Scripts.Interaction.States
{
    /// <summary>
    /// Represents the transform states of a single finger,
    /// including its metacarpal, proximal, intermediate, and distal joints.
    /// </summary>
    public struct FingerState
    {
        /// <summary>
        /// The transform state of the metacarpal (palm) bone of the finger.
        /// </summary>
        public TransformState Metacarpal;

        /// <summary>
        /// The transform state of the proximal (base) joint of the finger.
        /// </summary>
        public TransformState Proximal;
        
        /// <summary>
        /// The transform state of the intermediate (middle) joint of the finger.
        /// </summary>
        public TransformState Intermediate;
        
        /// <summary>
        /// The transform state of the distal (tip) joint of the finger.
        /// </summary>
        public TransformState Distal;
    }
    
    /// <summary>
    /// Represents the hand pose,
    /// including wrist and all five fingers (thumb, index, middle, ring, pinky).
    /// </summary>
    public struct HandState
    {
        /// <summary>
        /// The transform state of the wrist.
        /// </summary>
        public TransformState Wrist;

        /// <summary>
        /// The transform states for the thumb finger.
        /// </summary>
        public FingerState Thumb;
        
        /// <summary>
        /// The transform states for the index finger.
        /// </summary>
        public FingerState Index;
        
        /// <summary>
        /// The transform states for the middle finger.
        /// </summary>
        public FingerState Middle;
        
        /// <summary>
        /// The transform states for the ring finger.
        /// </summary>
        public FingerState Ring;
        
        /// <summary>
        /// The transform states for the pinky finger.
        /// </summary>
        public FingerState Pinky;
    }
}