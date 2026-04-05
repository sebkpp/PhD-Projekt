using System.Collections;
using System.Collections.Generic;
using Application.Scripts.Feedback.Data;
using Application.Scripts.Network.Experiment;
using UnityEngine;
using UnityEngine.Networking;

namespace Application.Scripts.Feedback
{
    /// <summary>
    /// Scene-level singleton. Fetches all slot stimuli from GET /trials/{trialId}/stimuli
    /// when the experiment becomes ready. Provides GetStimuli(slot) to other components.
    /// </summary>
    public class StimulusConfigLoader : MonoBehaviour
    {
        [SerializeField] private ExperimentContext _experimentContext;

        private readonly Dictionary<int, StimulusSlotConfig> _configBySlot = new();
        private string _baseUrl;

        private void Awake()
        {
            if (_experimentContext == null)
                _experimentContext = FindFirstObjectByType<ExperimentContext>();
        }

        private void OnEnable()
        {
            if (_experimentContext != null)
                _experimentContext.OnExperimentReady.AddListener(OnExperimentReady);
        }

        private void OnDisable()
        {
            if (_experimentContext != null)
                _experimentContext.OnExperimentReady.RemoveListener(OnExperimentReady);
        }

        private void OnExperimentReady(int trialId, Dictionary<int, string> slotGender)
        {
            _baseUrl = _experimentContext.BackendBaseUrl;
            StartCoroutine(FetchStimuli(trialId));
        }

        private IEnumerator FetchStimuli(int trialId)
        {
            string url = $"{_baseUrl}/trials/{trialId}/stimuli";
            using var req = UnityWebRequest.Get(url);
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"[StimulusConfigLoader] Failed to fetch stimuli: {req.error}");
                yield break;
            }

            var slots = StimulusSlotConfig.ParseArray(req.downloadHandler.text);
            _configBySlot.Clear();
            foreach (var slot in slots)
                _configBySlot[slot.slot] = slot;

            Debug.Log($"[StimulusConfigLoader] Loaded stimuli for {_configBySlot.Count} slots.");
        }

        /// <summary>Returns the stimulus config for a slot, or null if not yet loaded.</summary>
        public StimulusSlotConfig GetStimuli(int slot)
        {
            _configBySlot.TryGetValue(slot, out var config);
            return config;
        }

        public bool IsLoaded => _configBySlot.Count > 0;
    }
}
