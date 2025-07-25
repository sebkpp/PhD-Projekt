using UnityEngine;

namespace Application.Scripts.Utils.Test
{
    [ExecuteInEditMode]
    public class RotationViewer : MonoBehaviour
    {
        [SerializeField] private Vector3 globalRotation;

        // Update is called once per frame
        void Update()
        {
            globalRotation = transform.rotation.eulerAngles;
        }
    }
}
