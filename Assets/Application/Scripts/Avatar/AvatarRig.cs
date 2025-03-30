using System;
using Application.Scripts.Network.Input;
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

        public FingerState FingerState
        {
            set
            {
                proximal.SetLocalPositionAndRotation(value.Proximal.Position, value.Proximal.Rotation);
                intermediate.SetLocalPositionAndRotation(value.Intermediate.Position, value.Intermediate.Rotation);
                distal.SetLocalPositionAndRotation(value.Distal.Position, value.Distal.Rotation);
            }
        }
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
        
        public HandState HandState
        {
            set
            {
                thumb.FingerState = value.Thumb;
                index.FingerState = value.Index;
                middle.FingerState = value.Middle;
                ring.FingerState = value.Ring;
                pinky.FingerState = value.Pinky;
            }
        }
    }
}