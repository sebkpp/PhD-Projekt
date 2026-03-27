using System.Collections;
using Unity.XR.CoreUtils;
using UnityEngine;

namespace Application.Scripts.VR
{
    public class ReCenter : MonoBehaviour
    {
        [SerializeField] private Transform spawnPosition;
        [SerializeField] private Transform player;

        private void Start()
        {
            StartCoroutine(Compensate());
        }

        IEnumerator Compensate()
        {
            yield return new WaitForSeconds(1f);
            XROrigin xrRig = player.GetComponentInChildren<XROrigin>();
            Vector3 eyePosition = xrRig.Camera.transform.position;

            xrRig.Origin.transform.position -= (eyePosition - spawnPosition.position);
            Debug.Log(xrRig.Camera.transform.position);
        }
    }
}
