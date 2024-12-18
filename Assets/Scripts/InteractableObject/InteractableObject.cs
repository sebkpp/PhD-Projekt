using Fusion;
using UnityEngine;

namespace InteractableObject
{
    public class InteractableObject : NetworkBehaviour
    {
        private ChangeDetector _changes;
        private PlayerRef _currentOwner;
        
        [Networked] public int State { get; set; }

        public PlayerRef CurrentOwner { get; private set; }

        private Transform _followTransform;
        private bool _isHeld = false;

        public override void FixedUpdateNetwork()
        {
            if (Object.HasStateAuthority && _isHeld && _followTransform != null)
            {
                // Synchronisiere das Objekt mit der Hand des Halters
                transform.position = _followTransform.position;
                transform.rotation = _followTransform.rotation;
            }
        }

        public void Grab(PlayerRef newOwner, Transform handTransform)
        {
            if (Object.HasStateAuthority || Object.HasInputAuthority)
            {
                RPC_SetOwner(newOwner);
                _followTransform = handTransform;
                _isHeld = true;
            }
        }

        public void Release()
        {
            if (Object.HasStateAuthority || Object.HasInputAuthority)
            {
                _followTransform = null;
                _isHeld = false;
            }
        }

        [Rpc(RpcSources.InputAuthority, RpcTargets.StateAuthority)]
        private void RPC_SetOwner(PlayerRef newOwner)
        {
            CurrentOwner = newOwner;
        }

        // This method is called when the ownership of this object changes
        private void HandleOwnerChanged(PlayerRef previousOwner, PlayerRef newOwner)
        {
            if (newOwner == Runner.LocalPlayer)
            {
                // Assign input authority to the local player
                Object.AssignInputAuthority(newOwner);
            }
            else
            {
                // Remove input authority if no longer owned by the local player
                Object.RemoveInputAuthority();
            }
        }
    }
}

