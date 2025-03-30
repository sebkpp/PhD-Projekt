using Application.Scripts.Network.Input;
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
        public IHandRepresentation localRepresentation;
        public HandTrackingData HandTrackingData;
        
        private void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            // Find any children that can handle hand representation (we will forward hand commands to it)
            localRepresentation = GetComponentInChildren<IHandRepresentation>();
        }

        protected virtual void Update()
        {
            // If a local hand representation is available, we forward the input to it
            //  Note that the hand local representation is also used to store the finger colliders, and so need to be animated even if not having an actively displayed renderer
            if (localRepresentation != null)
            {
                //localRepresentation.SetHandCommand(handCommand);
            }
        }
    }
}