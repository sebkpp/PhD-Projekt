using System.Collections;
using Application.Scripts.Avatar;
using UnityEngine;

namespace Experiment.Utils.Location
{
    public class Replace : MonoBehaviour
    {
        [SerializeField] private HardwareRig localXRRig;
        [SerializeField] private Transform spawnPosition;
        [SerializeField] private Vector3 spawnOffset;

        private void Start()
        {
            StartCoroutine(Recenter(1000));
        }

        IEnumerator Recenter(int delay)
        {
            yield return new WaitForSeconds(delay/1000f);

            Vector3 headPosition = localXRRig.headset.transform.position;

            Vector3 headToSpawnPositionOffset = headPosition - spawnPosition.position;
            transform.position -= headToSpawnPositionOffset + spawnOffset;
            
            // Vector3 eyePosition = headPosition;
            // Vector3 offset = (eyePosition - spawnPosition.position);
            //
            // transform.position = transform.position - offset + spawnOffset;
        }
    }
}