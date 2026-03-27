using System.Collections;
using System.Collections.Generic;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network
{
    [RequireComponent(typeof(NetworkTransform))]
    public class NetworkFinger : NetworkBehaviour
    {
        //public const int EXECUTION_ORDER = NetworkRig.EXECUTION_ORDER + 10;

        [HideInInspector]
        public NetworkTransform networkTransform;

        private void Awake()
        {
            if (networkTransform == null) networkTransform = GetComponent<NetworkTransform>();
        }
    }
}
