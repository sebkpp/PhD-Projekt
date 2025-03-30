using Application.Scripts.Avatar_rigging;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Avatar.Utils
{
    /// <summary>
    /// Places the Avatar to the ground-floor and sets the VR-Hmd Position to its Avatar Head
    /// </summary>
    public class XRAvatarPositionAdjustment : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform vrHeadset;
        [SerializeField] private Transform xrRig;
        [SerializeField] private LayerMask groundLayer;

        [SerializeField] private UnityEvent<Vector3> avatarPositionChanged;
        
        /// <summary>
        /// Places the avatar to ground and moves the VR-Hmd Position to the head of its avatar
        /// </summary>
        /// <param name="avatar"></param>
        public void AdjustAvatarHeight(AvatarLookup avatar)
        {
            xrRig.position = avatar.AvatarRoot.position;
            xrRig.rotation = avatar.AvatarRoot.rotation;
            
            // Set Avatar to Ground
            float groundHeight = GetGroundHeight(avatar.AvatarRoot.position);
            float feetOffset = avatar.AvatarFeet.position.y - avatar.AvatarRoot.position.y;
        
            Vector3 newAvatarPosition = new Vector3(
                vrHeadset.position.x,  
                groundHeight-feetOffset, 
                vrHeadset.position.z
            );
        
            avatar.AvatarRoot.position = newAvatarPosition;
            
            // Adjust XR-Rig 
            Vector3 headOffset = avatar.AvatarMiddleEye.position - vrHeadset.position;
            Vector3 headsetOffset = xrRig.position + headOffset;
            
            xrRig.position = headsetOffset;
            
            avatarPositionChanged.Invoke(xrRig.position - newAvatarPosition);
        }
    
        /// <summary>
        /// Performs a raycast down to find ground-level
        /// </summary>
        /// <param name="position">Position from to find ground-level</param>
        /// <returns>ground-level</returns>
        private float GetGroundHeight(Vector3 position)
        {
            Vector3 origin = position + Vector3.up * 1f;
            
            if (Physics.Raycast(origin, Vector3.down, out var hit, 5f, groundLayer))
            {
                return hit.point.y;
            }
        
            Debug.LogWarning("XRAvatarHeightAdjustment: No floor found!");
            return position.y;
        }
    }
}
