using Fusion;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class HardwareHand : MonoBehaviour
    {
        public RigPart side;
        //public HandCommand handCommand;
        public bool isGrabbing = false;
        
        public NetworkTransform networkTransform;
        public HandTrackingData HandTrackingData;
        
        private void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            // Find any children that can handle hand representation (we will forward hand commands to it)
        }
    }
}