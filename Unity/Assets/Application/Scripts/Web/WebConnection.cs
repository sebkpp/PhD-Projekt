using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace Application.Scripts.Web
{
    [System.Serializable]
    class PlayerInfo { public string player_id; }
    public class WebConnection : MonoBehaviour
    {
        public string playerId = "Player123";
        public string joinUrl = "http://192.168.0.10:5000/join";
        public string heartbeatUrl = "http://192.168.0.10:5000/heartbeat";

        void Start()
        {
            StartCoroutine(SendPlayerEvent(joinUrl, "joined"));
            InvokeRepeating(nameof(SendHeartbeat), 5f, 5f); // alle 5 Sekunden
        }

        void SendHeartbeat()
        {
            StartCoroutine(SendPlayerEvent(heartbeatUrl, "heartbeat"));
        }

        IEnumerator SendPlayerEvent(string url, string action)
        {
            var json = JsonUtility.ToJson(new PlayerInfo { player_id = playerId });
            var request = new UnityWebRequest(url, "POST");
            byte[] body = System.Text.Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(body);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
                Debug.Log($"📤 Spieler {action}: {playerId}");
            else
                Debug.LogWarning($"❌ Fehler bei {action}: {request.error}");
        }
    }
}
