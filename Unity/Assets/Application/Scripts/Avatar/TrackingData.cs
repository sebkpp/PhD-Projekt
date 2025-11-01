using System;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Stores transform tracking data for a single finger.
    /// </summary>
    [Serializable]
    public class FingerTrackingData
    {
        /// <summary>
        /// Tracking data for the proximal bone of the finger.
        /// </summary>
        public TrackingData proximal;
        
        /// <summary>
        /// Tracking data for the intermediate bone of the finger.
        /// </summary>
        public TrackingData intermediate;
        
        /// <summary>
        /// Tracking data for the distal bone of the finger.
        /// </summary>
        public TrackingData distal;
        
        /// <summary>
        /// Gets the current transform state of this finger's bones.
        /// </summary>
        /// <returns>A <see cref="FingerState"/> object with position and rotation of each finger segment.</returns>
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

        /// <summary>
        /// Applies a <see cref="FingerState"/> to this finger's bones using the specified tracking offsets.
        /// </summary>
        /// <param name="state">The finger state to apply.</param>
        /// <param name="offsets">The offsets to apply to the tracking data.</param>
        public void SetFingerState(FingerState state, FingerOffsets offsets)
        {
            Quaternion fingerOffsetAxis = offsets.OffsetAxis;
            
            proximal.SetState(state.Proximal, offsets.proximal, fingerOffsetAxis);
            intermediate.SetState(state.Intermediate, offsets.intermediate, fingerOffsetAxis);
            distal.SetState(state.Distal, offsets.distal, fingerOffsetAxis);
        }
    }
    
    /// <summary>
    /// Stores transform tracking data for the full hand, including fingers and wrist.
    /// </summary>
    [Serializable]
    public class HandTrackingData
    {
        /// <summary>
        /// Tracking data for the wrist.
        /// </summary>
        public TrackingData wrist;
        
        /// <summary>
        /// Tracking data for the thumb.
        /// </summary>
        public FingerTrackingData thumb;
        
        /// <summary>
        /// Tracking data for the index.
        /// </summary>
        public FingerTrackingData index;
        
        /// <summary>
        /// Tracking data for the middle.
        /// </summary>
        public FingerTrackingData middle;
        
        /// <summary>
        /// Tracking data for the ring.
        /// </summary>
        public FingerTrackingData ring;
        
        /// <summary>
        /// Tracking data for the pinky.
        /// </summary>
        public FingerTrackingData pinky;
        
        /// <summary>
        /// Gets the current state of the entire hand.
        /// </summary>
        /// <returns>A <see cref="HandState"/> containing the wrist and all finger states.</returns>
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

        /// <summary>
        /// Applies a <see cref="HandState"/> to this hand using the provided offset configuration.
        /// </summary>
        /// <param name="handState">The hand state to apply.</param>
        /// <param name="handOffsets">Offset configuration for wrist and fingers.</param>
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
    
    /// <summary>
    /// Tracks and applies transform state for a single bone or joint.
    /// </summary>
    [Serializable]
    public class TrackingData
    {
        /// <summary>
        /// The source transform being tracked and updated.
        /// </summary>
        public Transform source;
        
        /// <summary>
        /// Gets the current position and rotation of the source as a <see cref="TransformState"/>.
        /// </summary>
        /// <returns>A <see cref="TransformState"/> representing the current transform.</returns>
        public TransformState GetState()
        {
            TransformState state = new TransformState()
            {
                Position = source.position,
                Rotation = source.rotation
            };
            
            return state;
        }

        /// <summary>
        /// Applies a transform state and positional/rotational offsets to the source.
        /// </summary>
        /// <param name="state">The target transform state.</param>
        /// <param name="offset">The positional and rotational offset to apply.</param>
        public void SetState(TransformState state, TrackingOffsets offset)
        {
            ApplyTransformOffset(state, offset, Quaternion.identity);
        }
        
        /// <summary>
        /// Applies a transform state and positional/rotational offsets to the source with a custom axis offset.
        /// </summary>
        /// <param name="state">The target transform state.</param>
        /// <param name="offset">The positional and rotational offset to apply.</param>
        /// <param name="offsetAxis">Additional rotational axis offset to apply.</param>
        public void SetState(TransformState state, TrackingOffsets offset, Quaternion offsetAxis)
        {
            ApplyTransformOffset(state, offset, offsetAxis);
        }

        /// <summary>
        /// Applies the given transform state and offsets to the source transform.
        /// </summary>
        /// <param name="state">The desired world transform state.</param>
        /// <param name="offset">Offsets to apply to position and rotation.</param>
        /// <param name="offsetAxis">Additional axis offset for rotation.</param>
        private void ApplyTransformOffset(TransformState state, TrackingOffsets offset, Quaternion offsetAxis)
        {
            if (source == null)
            {
                Debug.LogWarning("TrackingData source is null – skipping SetState.");
                return;
            }

            if (source.parent == null)
            {
                Debug.LogWarning($"TrackingData source '{source.name}' has no parent – skipping SetState.");
                return;
            }
            
            Quaternion offsetRotation = Quaternion.Euler(offset.rotation);
            
            // Position is actually ignored if Multi-Parential Position Constrain is deactivated,
            // activating it results in Finger-streching
            Vector3 offsetWorldPos = state.Position + (state.Rotation * (offsetRotation * offset.position));
            Quaternion offsetWorldRot = state.Rotation * offsetRotation * offsetAxis;
            
            Vector3 localPos = source.parent.InverseTransformPoint(offsetWorldPos);
     
            source.SetPositionAndRotation(source.parent.TransformPoint(localPos), offsetWorldRot);
        }
    }
}