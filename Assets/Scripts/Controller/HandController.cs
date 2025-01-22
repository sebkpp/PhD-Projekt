/*
using Connection;
using UnityEngine;
public class HandController : MonoBehaviour
{
    public Transform handTransform;

    private InteractableObject.InteractableObject _heldObject;

    private void Update()
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
        if (_heldObject == null)
        {
            // Prüfe, ob ein greifbares Objekt in der Nähe ist
            Collider[] hitColliders = Physics.OverlapSphere(handTransform.position, 0.1f);
            foreach (var collider in hitColliders)
            {
                InteractableObject.InteractableObject interactable = collider.GetComponent<InteractableObject.InteractableObject>();
                if (interactable != null)
                {
                    interactable.Grab(ConnectionManager.Instance.GetRunner().LocalPlayer, handTransform);
                    _heldObject = interactable;
                    break;
                }
            }
        }
    }

    private void Release()
    {
        if (_heldObject != null)
        {
            _heldObject.Release();
            _heldObject = null;
        }
    }
}
*/
