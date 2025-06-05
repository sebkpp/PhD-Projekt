using Fusion;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class HardwareHand : MonoBehaviour
    {
        public RigPart side;
        public bool isGrabbing = false;
        
        public NetworkTransform networkTransform;
        public HandTrackingData HandTrackingData;
        
        private void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
        }
    }
}