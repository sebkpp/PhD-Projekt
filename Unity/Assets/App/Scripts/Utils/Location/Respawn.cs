using UnityEngine;

namespace Application.Scripts.Utils.Location
{
    public class Respawn : MonoBehaviour
    {
        [SerializeField] private string floorTag = "Floor";
        private Transform _startTransform;
        void Start()
        {
            _startTransform = transform;
        }
        private void OnTriggerEnter(Collider other)
        {
            Debug.Log($"collided with {other.tag}");
            if (!other.CompareTag(floorTag)) return;
            transform.SetPositionAndRotation(_startTransform.position, _startTransform.rotation);
        }
    }
}
