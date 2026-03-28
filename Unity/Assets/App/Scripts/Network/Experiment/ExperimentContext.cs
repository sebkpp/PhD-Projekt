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
    /// Decoupled from Fusion — knows nothing about networking.
    /// </summary>
    public class ExperimentContext : MonoBehaviour
    {
        [SerializeField] private string _backendBaseUrl = "http://localhost:5000";

        public UnityEvent<int, Dictionary<int, string>> OnExperimentReady = new();
        public UnityEvent<string> OnExperimentError = new();

        public int TrialId { get; private set; }
        public int ExperimentId { get; private set; }

        private Dictionary<int, string> _slotGender = new();

        private void Start()
        {
            StartCoroutine(FetchNextExperiment());
        }

        public string GetGender(int playerId)
        {
            _slotGender.TryGetValue(playerId, out string gender);
            return gender ?? "Female";
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

            ExperimentId = response.experiment_id;
            TrialId      = response.trial_id;
            _slotGender  = new Dictionary<int, string>();

            foreach (var slot in response.slots)
                _slotGender[slot.slot] = slot.gender;

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
            public int experiment_id;
            public int trial_id;
            public SlotEntry[] slots;
        }

        [Serializable]
        private class SlotEntry
        {
            public int slot;
            public string gender;
        }
    }
}
