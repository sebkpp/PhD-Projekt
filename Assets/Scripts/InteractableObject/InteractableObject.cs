using Fusion;
using UnityEngine;

public class InteractableObject : NetworkBehaviour
{
    [Networked(OnChanged = nameof(OnOwnerChanged))]
    public PlayerRef CurrentOwner { get; private set; }

    private Transform followTransform;
    private bool isHeld = false;

    public override void FixedUpdateNetwork()
    {
        if (Object.HasStateAuthority && isHeld && followTransform != null)
        {
            // Synchronisiere das Objekt mit der Hand des Halters
            transform.position = followTransform.position;
            transform.rotation = followTransform.rotation;
        }
    }

    public void Grab(PlayerRef newOwner, Transform handTransform)
    {
        if (Object.HasStateAuthority || Object.HasInputAuthority)
        {
            RPC_SetOwner(newOwner);
            followTransform = handTransform;
            isHeld = true;
        }
    }

    public void Release()
    {
        if (Object.HasStateAuthority || Object.HasInputAuthority)
        {
            followTransform = null;
            isHeld = false;
        }
    }

    [Rpc(RpcSources.InputAuthority, RpcTargets.StateAuthority)]
    private void RPC_SetOwner(PlayerRef newOwner)
    {
        CurrentOwner = newOwner;
    }

    private static void OnOwnerChanged(Changed<InteractableObject> changed)
    {
        if (changed.Behaviour.CurrentOwner == Runner.LocalPlayer)
        {
            changed.Behaviour.Object.AssignInputAuthority(Runner.LocalPlayer);
        }
        else
        {
            changed.Behaviour.Object.RemoveInputAuthority();
        }
    }
}
