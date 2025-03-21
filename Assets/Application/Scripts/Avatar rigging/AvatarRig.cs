using System;
using UnityEngine;

namespace Application.Scripts.Avatar_rigging
{
    /// <summary>
    /// Stores the transforms for a avatars finger phalanx
    /// </summary>
    [Serializable]
    public class FingerRig
    {
        public Transform proximal;
        public Transform intermediate;
        public Transform distal;
    }
    
    /// <summary>
    /// Stores the transform for a avatar hand
    /// </summary>
    [Serializable]
    public class HandRig
    {
        public Transform wrist;
        public FingerRig thumb;
        public FingerRig index;
        public FingerRig middle;
        public FingerRig ring;
        public FingerRig pinky;
    }
}