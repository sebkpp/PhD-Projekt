namespace Application.Scripts.Avatar.Utils
{
    /// <summary>
    /// Represents the primary 3D axes in both positive and negative directions.
    /// Useful for defining directional alignment or offset axes in 3D space.
    /// </summary>
    public enum Axis
    {
        /// <summary>
        /// Positive X-axis direction (right).
        /// </summary>
        X,

        /// <summary>
        /// Negative X-axis direction (left).
        /// </summary>
        XNeg,

        /// <summary>
        /// Positive Y-axis direction (up).
        /// </summary>
        Y,

        /// <summary>
        /// Negative Y-axis direction (down).
        /// </summary>
        YNeg,

        /// <summary>
        /// Positive Z-axis direction (forward).
        /// </summary>
        Z,

        /// <summary>
        /// Negative Z-axis direction (backward).
        /// </summary>
        ZNeg
    }
}