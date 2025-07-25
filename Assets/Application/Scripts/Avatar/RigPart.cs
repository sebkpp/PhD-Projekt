namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Enumerates the different components of a VR rig that can be identified.
    /// </summary>
    public enum RigPart
    {
        /// <summary>
        /// No rig part is specified. Used as a default or null-like value.
        /// </summary>
        None,
        
        /// <summary>
        /// Represents the VR headset or HMD (head-mounted display) component.
        /// </summary>
        Headset,
        
        /// <summary>
        /// Represents the left controller or hand of the VR rig.
        /// </summary>
        LeftController,
        
        /// <summary>
        /// Represents the right controller or hand of the VR rig.
        /// </summary>
        RightController,
        
        /// <summary>
        /// An undefined or unrecognized rig part.
        /// Can be used for error handling or fallback cases.
        /// </summary>
        Undefined
    }
}