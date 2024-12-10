using Fusion;
using UnityEngine;

public class HandController : MonoBehaviour
{
    public Transform handTransform;

    private InteractableObject heldObject;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.G)) // Simuliert Greifen in VR
        {
            TryGrab();
        }

        if (Input.GetKeyDown(KeyCode.R)) // Simuliert Loslassen in VR
        {
            Release();
        }
    }

    private void TryGrab()
    {
        if (heldObject == null)
        {
            // Prüfe, ob ein greifbares Objekt in der Nähe ist
            Collider[] hitColliders = Physics.OverlapSphere(handTransform.position, 0.1f);
            foreach (var collider in hitColliders)
            {
                InteractableObject interactable = collider.GetComponent<InteractableObject>();
                if (interactable != null)
                {
                    interactable.Grab(ConnectionManager.Instance.GetRunner().LocalPlayer, handTransform);
                    heldObject = interactable;
                    break;
                }
            }
        }
    }

    private void Release()
    {
        if (heldObject != null)
        {
            heldObject.Release();
            heldObject = null;
        }
    }
}
