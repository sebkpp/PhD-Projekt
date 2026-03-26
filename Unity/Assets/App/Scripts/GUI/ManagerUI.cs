using Application.Scripts.Avatar;
using Application.Scripts.Experiment;
using Application.Scripts.Network;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace Application.Scripts.GUI
{
    //TODO Finish experiment/Reset/Save Data
    public class ManagerUI : MonoBehaviour
    {
        [Header("Experiment Id")]
        [SerializeField] private TMP_InputField expIdInput;
        [SerializeField] private Button blockExpIdButton;

        [Header("Gender")]
        [SerializeField] private TMP_Dropdown genderP1Dropdown;
        [SerializeField] private TMP_Dropdown genderP2Dropdown;

        [Header("Variables")]
        [SerializeField] private TMP_Dropdown avatarVariablesDropdown;
        [SerializeField] private TMP_Dropdown handVisVariablesDropdown;

        [Header("Timer")]
        [SerializeField] private bool useTimer;
        [SerializeField] private ExperimentTimer timer;
        [SerializeField] private int experimentDuration = 3;
        [SerializeField] private TextMeshProUGUI timerText;

        [Header("Others")]
        [SerializeField] private Button startExpButton;
        [SerializeField] private Log logArea;

        private TextMeshProUGUI _timerButtonText;
        private bool _timerRunning, _timerFinished;
        private ExperimentController _expController;
        private void OnEnable()
        {
            //Start situation
            timer.gameObject.SetActive(useTimer);
            startExpButton.interactable = false;
            SetDropdownValues();

            //Events
            blockExpIdButton.onClick.AddListener(SetExperimentId);
            startExpButton.onClick.AddListener(OnStartExperiment);
            genderP1Dropdown.onValueChanged.AddListener((int v) => OnGenderChange(v, true));
            genderP2Dropdown.onValueChanged.AddListener((int v) => OnGenderChange(v, false));
            avatarVariablesDropdown.onValueChanged.AddListener(OnAvatarValuesChanged);
            handVisVariablesDropdown.onValueChanged.AddListener(OnHandVisualsChanged);

            //Refs
            _timerButtonText = startExpButton.GetComponentInChildren<TextMeshProUGUI>();
            _expController = FindFirstObjectByType<ExperimentController>();
        }
        private void SetExperimentId()
        {
            if (_expController == null)
            {
                Debug.LogError("Experiment Controller is null.");
                return;
            }

            string message;

            //Update experiment id
            if (int.TryParse(expIdInput.text, out int id))
            {
                if (_expController.SetExperimentId(id))
                {
                    // Block Input UI 
                    expIdInput.interactable = false;
                    blockExpIdButton.interactable = false;
                    message = "Experiment id saved!";

                    // Enable start exp
                    startExpButton.interactable = true;
                }
                else
                    message = $"Unvalid id. Input: {expIdInput.text}";
            }
            else
                message = $"Experiment id is not a number. Input: {expIdInput.text}";

            logArea.LogMessage(message);
        }
        private void OnStartExperiment()
        {
            startExpButton.interactable = false;
            _expController.StartExperiment();
        }
        public void LogMessage(string message)
        {
            logArea.LogMessage(message);
        }

        #region Change Experiment Variables
        private void SetDropdownValues()
        {
            //Delete template
            genderP1Dropdown.ClearOptions();
            genderP2Dropdown.ClearOptions();
            avatarVariablesDropdown.ClearOptions();
            handVisVariablesDropdown.ClearOptions();

            //Add gender options
            List<string> tempList = Enum.GetNames(typeof(Gender)).ToList();
            genderP1Dropdown.AddOptions(tempList);
            genderP2Dropdown.AddOptions(tempList);

            //Add avatar options
            tempList = Enum.GetNames(typeof(AvatarOptions)).ToList();
            avatarVariablesDropdown.AddOptions(tempList);

            //Add hand visuals options
            tempList = Enum.GetNames(typeof(HandVisuals)).ToList();
            handVisVariablesDropdown.AddOptions(tempList);

            //Preselect undefined gender
            int index = (int)Gender.Undefined;
            genderP1Dropdown.value = index;
            genderP2Dropdown.value = index;

            //Preselect only hands
            index = (int)AvatarOptions.Hands;
            avatarVariablesDropdown.value = index;

            //Preselect none as hand visuals
            index = (int)HandVisuals.None;
            handVisVariablesDropdown.value = index;
        }
        private void OnGenderChange(int value, bool playerOne)
        {
            if (_expController == null) return;
            // _expController.ChangePlayerGender(
            //     _playerManager.GetPlayerRefById(playerOne ? 2 : 3),
            //     (Gender)value);
        }
        private void OnAvatarValuesChanged(int value)
        {
            _expController.ChangeAvatarOptions((AvatarOptions)value);
        }
        private void OnHandVisualsChanged(int value)
        {
            _expController.ChangeHandVisuals((HandVisuals)value);
        }

        #endregion

        #region Timer
        private void HandleTimer()
        {
            //Pause experiment
            if (_timerRunning)
            {
                timer.StopStopwatch();
                _timerRunning = false;
                _timerButtonText.text = "Continue experiment";
            }
            //Experiment finished
            else if (_timerFinished)
            {
                timer.ResetStopwatch();
                _timerButtonText.text = "Start experiment";

                //Update experiment controller
                _timerFinished = false;
            }
            //Start/Continue experiment
            else
            {
                _timerFinished = false;
                _timerRunning = true;
                timer.StartStopwatch();
                StartCoroutine(UpdateTimerUI());
                _timerButtonText.text = "Stop experiment";
            }

        }
        private IEnumerator UpdateTimerUI()
        {
            TimeSpan time;

            while (timer.StopwatchIsRunning())
            {
                time = timer.GetTimeStopwatch();
                timerText.text = time.ToString(@"mm\:ss");

                if (time.TotalMinutes >= experimentDuration)
                {
                    timer.StopStopwatch();
                    _timerRunning = false;
                    _timerFinished = true;
                    HandleTimer();
                }

                yield return null;
            }
        }
        #endregion
    }
}