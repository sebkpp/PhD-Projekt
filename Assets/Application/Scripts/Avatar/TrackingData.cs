using System;
using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using Application.Scripts.Utils.Extensions;
using UnityEngine;
using UnityEngine.Serialization;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Stores the finger-tracking data
    /// </summary>
    [Serializable]
    public class FingerTrackingData
    {
        public TrackingData proximal;
        public TrackingData intermediate;
        public TrackingData distal;
        
        public FingerState GetFingerState()
        {
            FingerState state = new FingerState()
            {
                Proximal = proximal.GetLocalState(),
                Intermediate = intermediate.GetLocalState(),
                Distal = distal.GetLocalState()
            };

            return state;
        }

        public void SetFingerState(FingerState state)
        {
            proximal.SetLocalState(state.Proximal);
            intermediate.SetLocalState(state.Intermediate);
            distal.SetLocalState(state.Distal);
        }
    }
    
    /// <summary>
    /// Stores the hand-tracking data and offset adjustments
    /// </summary>
    [Serializable]
    public class HandTrackingData
    {
        public TrackingData wrist;
        
        public FingerTrackingData thumb;
        public FingerTrackingData index;
        public FingerTrackingData middle;
        public FingerTrackingData ring;
        public FingerTrackingData pinky;
        
        
        public HandState GetHandState()
        {
            HandState state = new HandState
            {
                Wrist = wrist.GetState(),
                Thumb = thumb.GetFingerState(),
                Index = index.GetFingerState(),
                Middle = middle.GetFingerState(),
                Ring = ring.GetFingerState(),
                Pinky = pinky.GetFingerState()
            };

            return state;
        }

        public void SetHandState(HandState handState)
        {
            wrist.SetState(handState.Wrist);
            
            thumb.SetFingerState(handState.Thumb);
            index.SetFingerState(handState.Index);
            middle.SetFingerState(handState.Middle);
            ring.SetFingerState(handState.Ring);
            pinky.SetFingerState(handState.Pinky);
        }
    }
    
    [Serializable]
    public class TrackingData
    {
        public Transform source;
        public Vector3 offsetPosition;
        public Vector3 offsetRotation;
        
        public TransformState GetState()
        {
            TransformState state = new TransformState()
            {
                Position = source.ApplyOffset(offsetPosition),
                Rotation = source.ApplyOffsetRotation(offsetRotation)
            };
            
            return state;
        }

        public TransformState GetLocalState()
        {
            TransformState state = new TransformState()
            {
                Position = source.localPosition,
                Rotation = source.ApplyOffsetRotation(offsetRotation)
            };

            return state;
        }

        public void SetState(TransformState state)
        {
            source.SetPositionAndRotation(state.Position, state.Rotation);
        }

        public void SetLocalState(TransformState state)
        {
            source.localPosition = state.Position;
            source.localRotation = state.Rotation;
        }
    }
}