using Application.Scripts.Interaction;
using Application.Scripts.Interaction.States;
using Application.Scripts.Utils.Extensions;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Represents the physical XR rig setup on the local device.
    /// Collects and provides positional and rotational tracking data
    /// from the local headset and controllers.
    /// </summary>
    public class HardwareRig : MonoBehaviour
    {
        /// <summary>
        /// Reference to the left hardware hand (controller).
        /// </summary>
        public HardwareHand leftHand;
        
        /// <summary>
        /// Reference to the right hardware hand (controller).
        /// </summary>
        public HardwareHand rightHand;
        
        /// <summary>
        /// Reference to the tracked headset.
        /// </summary>
        public HardwareHeadset headset;
        
        private Vector3 _playAreaOffsetPosition;
        
        /// <summary>
        /// Sets an offset that will be subtracted from the play area position.
        /// Useful for aligning virtual and physical spaces.
        /// </summary>
        /// <param name="offset">Offset vector to subtract from play area position.</param>
        public void SetXRRigOffset(Vector3 offset)
        {
            _playAreaOffsetPosition = offset;
        }

        /// <summary>
        /// Gets the current tracking state of the entire hardware rig, including
        /// play area position, headset, and both controllers.
        /// </summary>
        public virtual XRInputState RigState => new()
        {
            PlayArea = new TransformState
            {
                Position = transform.position - _playAreaOffsetPosition,
                Rotation = transform.rotation
            },
            Head = headset.transform.GetTransformState(),
            LeftHand = leftHand.HandTrackingData.GetHandPose(),
            RightHand = rightHand.HandTrackingData.GetHandPose()
        };
    }
}
