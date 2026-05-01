using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;


namespace Application.Scripts.GUI
{
    public class OnboardingUIController : MonoBehaviour
    {
        [HideInInspector] public static UnityEvent OnExperimentReady = new();
        [HideInInspector] public static UnityEvent OnExperimentNotReady = new();

        [Header("Buttons")]
        [SerializeField] private Button startButton;
        [SerializeField] private Button stopButton;

        #region Callbacks
        public void OnEnable()
        {
            startButton.onClick.AddListener(() => OnChangeOnboardingState(true));
            stopButton.onClick.AddListener(() => OnChangeOnboardingState(false));
        }

        public void OnDisable()
        {
            startButton.onClick.RemoveAllListeners();
            stopButton.onClick.RemoveAllListeners();
        }
        #endregion

        #region Private methods
        private void OnChangeOnboardingState(bool start)
        {
            stopButton.gameObject.SetActive(start);
            startButton.gameObject.SetActive(!start);

            //Let others know
            if (start)
                OnExperimentReady?.Invoke();
            else
                OnExperimentNotReady?.Invoke();
        }

        #endregion

        #region Testing
        [ContextMenu("Click Start Experiment")]
        private void StartExp()
        {
            OnChangeOnboardingState(true);
        }
        [ContextMenu("Click Stop Experiment")]
        private void StopExp()
        {
            OnChangeOnboardingState(false);
        }
        #endregion
    }

}