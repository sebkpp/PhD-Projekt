using Application.Scripts.Avatar;
using Fusion;
using UnityEngine;
using UnityEngine.Serialization;

namespace Application.Scripts.Network.Input
{
    public class NetworkHeadset : NetworkBehaviour
    {
        public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;
        
        [HideInInspector]
        public NetworkTransform networkTransform;

        private void Awake()
        {
            if (networkTransform == null) networkTransform = GetComponent<NetworkTransform>();
        }
    }
}