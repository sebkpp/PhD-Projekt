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

    }
}