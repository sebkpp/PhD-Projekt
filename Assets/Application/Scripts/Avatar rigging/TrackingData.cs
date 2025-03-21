using System;
using UnityEngine;

namespace Application.Scripts.Avatar_rigging
{
    /// <summary>
    /// Stores the finger phalanx tracking data and offset adjustments
    /// </summary>
    [Serializable]
    public class PhalanxTrackingData
    {
        public Transform source;
        public Vector3 offsetPosition;
        public Vector3 offsetRotation;
    }
    
    /// <summary>
    /// Stores the finger-tracking data
    /// </summary>
    [Serializable]
    public class FingerTrackingData
    {
        public PhalanxTrackingData proximal;
        public PhalanxTrackingData intermediate;
        public PhalanxTrackingData distal;
    }
    
    /// <summary>
    /// Stores the hand-tracking data and offset adjustments
    /// </summary>
    [Serializable]
    public class HandTrackingData
    {
        public Transform wristSource;
        public Vector3 offsetPosition;
        public Vector3 offsetRotation;

        public FingerTrackingData thumb;
        public FingerTrackingData index;
        public FingerTrackingData middle;
        public FingerTrackingData ring;
        public FingerTrackingData pinky;
    }
}