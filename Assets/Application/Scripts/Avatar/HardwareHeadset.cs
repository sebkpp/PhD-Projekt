using Fusion;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class HardwareHeadset: MonoBehaviour
    {
        //public Fader fader;
        public NetworkTransform networkTransform;
        
        private void Awake()
        {
            //if (fader == null) fader = GetComponentInChildren<Fader>();
            if (networkTransform == null) networkTransform = GetComponent<NetworkTransform>();
        }
    }
}