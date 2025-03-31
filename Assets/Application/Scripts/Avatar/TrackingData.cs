using System;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using Application.Scripts.Network.Input;
using UnityEngine;

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
                Proximal = proximal.GetState(),
                Intermediate = intermediate.GetState(),
                Distal = distal.GetState()
            };
            
            return state;
        }

        public void SetFingerState(FingerState state, FingerOffsets offsets)
        {
            proximal.SetState(state.Proximal, offsets.proximal);
            intermediate.SetState(state.Intermediate, offsets.intermediate);
            distal.SetState(state.Distal, offsets.distal);
        }
    }
    
    /// <summary>
    /// Stores the hand-tracking data and offset adjustments
    /// </summary>
    [Serializable]
    public class HandTrackingData
    {
        public FingerTrackingData thumb;
        public FingerTrackingData index;
        public FingerTrackingData middle;
        public FingerTrackingData ring;
        public FingerTrackingData pinky;
        
        
        public HandState GetHandPose()
        {
            HandState state = new HandState
            {
                Thumb = thumb.GetFingerState(),
                Index = index.GetFingerState(),
                Middle = middle.GetFingerState(),
                Ring = ring.GetFingerState(),
                Pinky = pinky.GetFingerState()
            };
            
            return state;
        }

        public void SetHandPose(HandState handState, HandOffsets handOffsets)
        {
            thumb.SetFingerState(handState.Thumb, handOffsets.thumb);
            index.SetFingerState(handState.Index, handOffsets.index);
            middle.SetFingerState(handState.Middle, handOffsets.middle);
            ring.SetFingerState(handState.Ring, handOffsets.ring);
            pinky.SetFingerState(handState.Pinky, handOffsets.pinky);
        }
    }
    
    [Serializable]
    public class TrackingData
    {
        public Transform source;
        
        public TransformState GetState()
        {
            TransformState state = new TransformState()
            {
                Position = source.position,
                Rotation = source.rotation
            };
            
            return state;
        }
        
        public TransformState GetLocalState()
        {
            TransformState state = new TransformState()
            {
                Position = source.position,
                Rotation = source.rotation
            };
            
            // state.Position += offset.position;
            // state.Rotation *= Quaternion.Euler(offset.rotation);
            //
            // TransformState stateLocal = new TransformState()
            // {
            //     Position = source.InverseTransformPoint(state.Position),
            //     Rotation = Quaternion.Inverse(source.rotation) * state.Rotation
            // };
            
            return state;
        }

        public void SetState(TransformState state, TrackingOffsets offset)
        {
            state.Position += offset.position;
            state.Rotation *= Quaternion.Euler(offset.rotation);
            
            source.SetPositionAndRotation(state.Position, state.Rotation);
        }
        
        public void SetLocalState(TransformState state)
        {
            //Quaternion offsetRotation = Quaternion.Euler(offset.rotation) * offsetAxis;
            source.position = state.Position;
            source.rotation = state.Rotation;
            //source.SetPositionAndRotation(state.Position, state.Rotation);
        }
    }
}