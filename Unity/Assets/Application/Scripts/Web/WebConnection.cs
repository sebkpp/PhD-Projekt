using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace Application.Scripts.Web
{
    public class WebConnection : MonoBehaviour
    {
        [Header("URL zum Testserver (z. B. https://webhook.site/xyz...)")]
        public string serverUrl = "https://yourserver.com/api/test";
        
        // Start is called once before the first execution of Update after the MonoBehaviour is created
        void Start()
        {
            SendTestData();
        }

        public void SendTestData()
        {
            StartCoroutine(PostTestData());
        }

        IEnumerator PostTestData()
        {
            WWWForm form = new WWWForm();
            form.AddField("playerId", "TestPlayer123");
            form.AddField("status", "connected");
            form.AddField("timestamp", System.DateTime.UtcNow.ToString("o"));

            using UnityWebRequest www = UnityWebRequest.Post(serverUrl, form);
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Fehler beim Senden: " + www.error);
            }
            else
            {
                Debug.Log("Erfolgreich gesendet!");
                Debug.Log("Antwort: " + www.downloadHandler.text);
            }
        }
    }
}
