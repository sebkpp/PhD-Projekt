using Fusion;
using UnityEngine;

public class AvatarMovement : NetworkBehaviour
{
    [SerializeField] private float _dragSpeed = 5f;
    private Camera _mainCamera;
    private bool _isDragging = false;
    private Vector3 _lastMousePosition;

    private void Start()
    {
        _mainCamera = Camera.main;
        Debug.Log($"<color=yellow>AvatarMovement started on {gameObject.name}</color>");
        Debug.Log($"<color=yellow>Has State Authority: {HasStateAuthority}</color>");
    }

    private void Update()
    {
        // nur bewegen, wenn authorität hat
        if (!HasStateAuthority)
        {
            // Debug 
            if (!_isDragging) 
                Debug.Log($"<color=red>No state authority on {gameObject.name}</color>");
            return;
        }

        if (Input.GetMouseButtonDown(0)) // linke maustaste
        {
            Ray ray = _mainCamera.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;
            Debug.Log($"<color=blue>Mouse clicked, casting ray</color>");

            if (Physics.Raycast(ray, out hit))
            {
                Debug.Log($"<color=blue>Hit something: {hit.collider.gameObject.name}</color>");
                if (hit.collider.gameObject == gameObject)
                {
                    _isDragging = true;
                    _lastMousePosition = Input.mousePosition;
                    Debug.Log($"<color=green>Started dragging {gameObject.name}</color>");
                }
            }
        }
        else if (Input.GetMouseButtonUp(0))
        {
            if (_isDragging)
                Debug.Log($"<color=yellow>Stopped dragging {gameObject.name}</color>");
            _isDragging = false;
        }

        if (_isDragging)
        {
            Vector3 delta = Input.mousePosition - _lastMousePosition;
            Vector3 movement = new Vector3(delta.x, 0, delta.y) * (_dragSpeed * Time.deltaTime);
            
            // Transform the movement to world space based on camera orientation
            movement = _mainCamera.transform.TransformDirection(movement);
            movement.y = 0; // Keep movement on the horizontal plane
            
            transform.position += movement;
            Debug.Log($"<color=cyan>Moving {gameObject.name}: {movement}</color>");
            
            _lastMousePosition = Input.mousePosition;
        }
    }
}