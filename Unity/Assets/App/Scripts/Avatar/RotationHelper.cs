using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class RotationHelper : MonoBehaviour
    {
        [field: SerializeField] public Transform ConstrainedHead { get; set; }
        [field: SerializeField] public Transform ConstrainedEye { get; set; }


        public void SetConstrains(Transform head, Transform eye)
        {
            ConstrainedHead = head;
            ConstrainedEye = eye;
        }
        
        private void FixedUpdate()
        {
            if (ConstrainedHead == null || ConstrainedEye == null) return;
            
            //ConstrainedHead.rotation = ConstrainedEye.rotation;
        }
    }
}