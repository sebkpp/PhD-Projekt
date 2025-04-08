namespace Application.Scripts.Interaction.States
{
    /// <summary>
    /// Saves an Input-State. contains Position/Rotation of PlayerArea, Head, Left and Right Hand
    /// </summary>
    public struct XRInputState
    {
        // Player Area, e.g., for teleportation
        public TransformState PlayArea { get; set; }
        
        // Head
        public TransformState Head { get; set; }
        
        // Left Hand
        public HandState LeftHand { get; set; }

        // Right Hand
        public HandState RightHand { get; set; }

    }
}