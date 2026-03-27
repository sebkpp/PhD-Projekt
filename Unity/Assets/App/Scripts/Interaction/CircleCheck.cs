using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Interaction
{
    public class CircleCheck : MonoBehaviour
    {
        [SerializeField] private UnityEvent objectPlaced;

        [SerializeField] private LayerMask objectLayers;

        private bool _isObjectInCircle;

        public bool IsObjectInCircle
        {
            get => _isObjectInCircle;
            set => _isObjectInCircle = value;
        }

        private void OnTriggerEnter(Collider other)
        {
            if ((objectLayers.value & (1 << other.gameObject.layer)) <= 0) return;
            if (_isObjectInCircle) return;
            
            objectPlaced?.Invoke();
            _isObjectInCircle = true;
        }
    }
}
