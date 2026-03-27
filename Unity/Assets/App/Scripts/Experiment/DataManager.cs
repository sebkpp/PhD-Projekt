using System;
using System.Collections.Generic;
using System.IO;
using Application.Scripts;
using UnityEngine;

namespace Application.Scripts.Experiment
{
    public class DataManager : MonoBehaviour
    {
        [SerializeField] private TrialDataController trial;
        [SerializeField] private GameManager gameManager;

        private List<EyeTrackingData> _eyeTrackingDataList = new();

        public void OnEyesTracked(TrackedLayers layers)
        {
            int playerId = gameManager.LocalPlayerObject.PlayerId;
            EyeTrackingData trackingData = new()
            {
                TrialId = trial.TrialId,
                PlayerId = playerId,
                PlayerRole = trial.GetPlayerRole(playerId),
                Phase = trial.Phase,
                TrackedLayers = layers,
                Timestamp = DateTime.Now.ToString("yyyy-MM-dd \\ THH:mm:ss"),
            };

            _eyeTrackingDataList.Add(trackingData);
        }


        //When experiment ends, save data
        public void SaveData()
        {
            EyeTrackingDataRoot eyeTrackingRoot = new()
            {
                Data = _eyeTrackingDataList.ToArray()
            };    
        
            string path = Path.Combine(UnityEngine.Application.persistentDataPath, "EyeTrackingData.json");
            string data = JsonUtility.ToJson(eyeTrackingRoot);

            try
            {
                File.WriteAllText(path, data);
                Debug.Log($"Data saved successfully in {path}");
            }
            catch (Exception ex)
            {
                Debug.LogError(ex.ToString());
            }
        }
        private void OnDisable()
        {
            SaveData();
        }

    }
}