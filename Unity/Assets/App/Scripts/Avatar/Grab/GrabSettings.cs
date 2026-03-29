using UnityEngine;

namespace Application.Scripts.Avatar.Grab
{
    [CreateAssetMenu(fileName = "GrabSettings", menuName = "ManualStudy/GrabSettings")]
    public class GrabSettings : ScriptableObject
    {
        [Tooltip("Effective grip must exceed this to initiate a grab.")]
        public float grabThreshold = 0.7f;

        [Tooltip("Effective grip must drop below this to release (hysteresis).")]
        public float releaseThreshold = 0.3f;

        [Tooltip("Sum of both players' effective grips below this causes the object to fall.")]
        public float dropThreshold = 0.4f;

        [Tooltip("Spring constant for the virtual grip spring (N/m).")]
        public float springConstant = 800f;

        [Tooltip("Damping factor applied to object velocity.")]
        public float damping = 12f;

        [Tooltip("Max distance (metres) at which grip remains effective. Beyond this grip strength = 0.")]
        public float maxGripReach = 0.15f;

        [Tooltip("Max fraction of the hand blend toward the object during tug (0 = no blend, 1 = full).")]
        public float maxHandBlend = 0.3f;

        [Tooltip("Radius of each fingertip sphere collider (metres).")]
        public float fingertipRadius = 0.012f;
    }
}
