using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;

namespace Application.Scripts.Network.Experiment
{
    /// <summary>
    /// Fetches the next open experiment from the Web backend at startup.
    /// Fires OnExperimentReady when data is available, OnExperimentError on failure.
    /// </summary>
    public class ExperimentContext : MonoBehaviour
    {
        [SerializeField] private string _backendBaseUrl = "http://localhost:5000";

        [SerializeField] private UnityEvent<int, Dictionary<int, string>> OnExperimentReady = new();
        [SerializeField] private UnityEvent<string> OnExperimentError = new();

        public int    TrialId      { get; private set; }
        public int    ExperimentId { get; private set; }
        public string BackendBaseUrl => _backendBaseUrl;

        private Dictionary<int, string> _slotGender      = new();
        private Dictionary<int, int>    _slotParticipant = new();

        private void Start()
        {
            StartCoroutine(FetchNextExperiment());
        }

        public string GetGender(int playerId)
        {
            _slotGender.TryGetValue(playerId, out string gender);
            return gender ?? "Female";
        }

        /// <summary>
        /// Returns the participant_id for the given Fusion PlayerId (mapped via slot index).
        /// Returns -1 if not found.
        ///
        /// ASSUMPTION: Fusion assigns PlayerId values starting from 1, matching the slot numbers
        /// (1 and 2) returned by /experiments/next. If the host is PlayerId 0 or slot numbers
        /// differ from Fusion's assignment, this mapping will silently return -1.
        /// </summary>
        public int GetParticipantId(int playerId)
        {
            return _slotParticipant.TryGetValue(playerId, out int participantId) ? participantId : -1;
        }

        /// <summary>
        /// Returns the slot number (1 or 2) for the given Fusion PlayerId.
        /// Returns -1 if not found.
        /// Relies on the assumption that Fusion PlayerId == slot number.
        /// </summary>
        public int GetSlot(int fusionPlayerId)
        {
            return _slotParticipant.ContainsKey(fusionPlayerId) ? fusionPlayerId : -1;
        }

        public void FinishTrial()
        {
            if (TrialId > 0)
                StartCoroutine(PostFinishTrial(TrialId));
        }

        private IEnumerator FetchNextExperiment()
        {
            string url = $"{_backendBaseUrl}/experiments/next";
            using var request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                string msg = $"[ExperimentContext] Failed to fetch experiment: {request.error}";
                Debug.LogError(msg);
                OnExperimentError.Invoke(msg);
                yield break;
            }

            var response = JsonUtility.FromJson<ExperimentNextResponse>(request.downloadHandler.text);
            if (response == null)
            {
                string msg = "[ExperimentContext] Failed to parse experiment response.";
                Debug.LogError(msg);
                OnExperimentError.Invoke(msg);
                yield break;
            }

            ExperimentId     = response.experiment_id;
            TrialId          = response.trial_id;
            _slotGender      = new Dictionary<int, string>();
            _slotParticipant = new Dictionary<int, int>();

            if (response.slots == null)
            {
                string msg = "[ExperimentContext] Response has no slot data.";
                Debug.LogError(msg);
                OnExperimentError.Invoke(msg);
                yield break;
            }
            foreach (var slot in response.slots)
            {
                _slotGender[slot.slot]      = slot.gender;
                _slotParticipant[slot.slot] = slot.participant_id;
            }

            Debug.Log($"<color=#ADD8E6>[ExperimentContext]</color> Experiment {ExperimentId}, Trial {TrialId} ready.");
            OnExperimentReady.Invoke(TrialId, _slotGender);
        }

        private IEnumerator PostFinishTrial(int trialId)
        {
            string url = $"{_backendBaseUrl}/trials/{trialId}/end";
            using var request = new UnityWebRequest(url, "POST");
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[ExperimentContext] Failed to finish trial {trialId}: {request.error}");
            else
                Debug.Log($"<color=#ADD8E6>[ExperimentContext]</color> Trial {trialId} finished.");
        }

        [Serializable]
        private class ExperimentNextResponse
        {
            public int        experiment_id;
            public int        trial_id;
            public SlotEntry[] slots;
        }

        [Serializable]
        private class SlotEntry
        {
            public int    slot;
            public string gender;
            public int    participant_id;
        }
    }
}
