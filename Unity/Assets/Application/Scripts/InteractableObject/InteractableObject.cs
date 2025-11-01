using Fusion;
using UnityEngine;

namespace InteractableObject
{
    public class InteractableObject : NetworkBehaviour
    {
        [Networked] public PlayerRef CurrentOwner { get; private set; }
        [Networked] public int State { get; private set; }

        private Transform _followTransform;
        private bool _isHeld;

        public override void FixedUpdateNetwork()
        {
            if (Object.HasStateAuthority && _isHeld && _followTransform != null)
            {
                transform.position = _followTransform.position;
                transform.rotation = _followTransform.rotation;
            }
        }

        public void Grab(PlayerRef owner, Transform handTransform)
        {
            if (Object.HasStateAuthority)
            {
                _followTransform = handTransform;
                _isHeld = true;
                RPC_SetOwner(owner);
            }
        }

        public void Release()
        {
            if (Object.HasStateAuthority)
            {
                _followTransform = null;
                _isHeld = false;
            }
        }

        [Rpc(RpcSources.InputAuthority, RpcTargets.StateAuthority)]
        private void RPC_SetOwner(PlayerRef owner)
        {
            CurrentOwner = owner;
        }
    }
}


