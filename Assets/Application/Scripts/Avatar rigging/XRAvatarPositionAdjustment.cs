using UnityEngine;

namespace Application.Scripts.Avatar_rigging
{
    /// <summary>
    /// Places the Avatar to the groundfloor and sets the VR-Glass Position to its Avatar Head
    /// </summary>
    public class XRAvatarPositionAdjustment : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform vrHeadset;
        [SerializeField] private Transform xrRig;
        [SerializeField] private LayerMask groundLayer; 

        public void AdjustAvatarHeight(AvatarLookup avatar)
        {
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
        }
    
        private float GetGroundHeight(Vector3 position)
        {
            if (Physics.Raycast(position + Vector3.up * 1f, Vector3.down, out var hit, 5f, groundLayer))
            {
                return hit.point.y;
            }
        
            Debug.LogWarning("XRAvatarHeightAdjustment: No floor found!");
            return position.y;
        }
    }
}
