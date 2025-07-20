using System;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
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
            Quaternion fingerOffsetAxis = offsets.OffsetAxis;
            
            proximal.SetState(state.Proximal, offsets.proximal, fingerOffsetAxis);
            intermediate.SetState(state.Intermediate, offsets.intermediate, fingerOffsetAxis);
            distal.SetState(state.Distal, offsets.distal, fingerOffsetAxis);
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
        
        
        public HandState GetHandPose()
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

        public void SetHandPose(HandState handState, HandOffsets handOffsets)
        {
            wrist.SetState(handState.Wrist, handOffsets.wrist);
            
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

        public void SetState(TransformState state, TrackingOffsets offset)
        {
            Quaternion offsetRotation = Quaternion.Euler(offset.rotation);
            Vector3 offsetWorldPos = state.Position + (state.Rotation * (offsetRotation * offset.position));
            Quaternion offsetWorldRot = state.Rotation * offsetRotation;

            Vector3 localPos = source.parent.InverseTransformPoint(offsetWorldPos);
     
            source.SetPositionAndRotation(source.parent.TransformPoint(localPos), offsetWorldRot);
        }
        
        public void SetState(TransformState state, TrackingOffsets offset, Quaternion offsetAxis)
        {
            Quaternion offsetRotation = Quaternion.Euler(offset.rotation);
            // Position is actually ignored if Multi-Parential Position Constrain is deactivated,
            // activating it results in Finger-streching
            Vector3 offsetWorldPos = state.Position + (state.Rotation * (offsetRotation * offset.position));
            Quaternion offsetWorldRot = state.Rotation * offsetRotation * offsetAxis;

            Vector3 localTargetPosition = source.parent.InverseTransformPoint(offsetWorldPos);
            
            source.SetPositionAndRotation(
                source.parent.TransformPoint(localTargetPosition), 
                offsetWorldRot);
        }
        
        
    }
}