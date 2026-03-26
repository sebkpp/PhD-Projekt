using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace Application.Scripts.Experiment
{
    public class GazeInputController : MonoBehaviour
    {
        private UnityEngine.XR.Interaction.Toolkit.Interactors.XRGazeInteractor gazeInteractor;

        private void Start()
        {
            gazeInteractor = GetComponent<UnityEngine.XR.Interaction.Toolkit.Interactors.XRGazeInteractor>();
        }
        void Update()
        {
            if (gazeInteractor == null) return;

            if (gazeInteractor.TryGetCurrent3DRaycastHit(out RaycastHit res))
            {                
                Debug.Log("HIT:" + res.transform.gameObject.name);
            }
        }
    }
}